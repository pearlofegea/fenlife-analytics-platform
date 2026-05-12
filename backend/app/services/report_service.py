"""
Rapor üretim pipeline.

Sprint 2 (mevcut): PDF'ler gerçekten parse edilir, student_data gerçek veri içerir.

Akış:
  1. parse_uploaded_files()  → NormalizedExamResult listesi
  2. normalized_to_exam_dict() → exam dict listesi
  3. resolve_student_identity() → öğrenci adı + sınıf
  4. build_student_data()    → generator'ın beklediği student_data
  5. generate_all_charts()   → PNG'ler
  6. generate_report()       → DOCX
  7. update_status("completed")

Hata durumu:
  - Hiçbir PDF parse edilemezse job "failed" olur, hata mesajı DB'ye yazılır.
  - Bazı PDF'ler başarısızsa parse olan kısımla devam edilir (kısmi sonuç).
"""
import logging

from app.config import settings
from app.db.session import SessionLocal
from app.parser.pipeline import (
    ParsePipelineError,
    normalized_to_exam_dict,
    parse_uploaded_files,
    resolve_student_identity,
)
from app.repositories import report_job_repo, student_repo
from app.report.analytics import build_student_data
from app.report.charts import generate_all_charts
from app.report.generator import generate_report

logger = logging.getLogger(__name__)


def run_pipeline(job_id: str, file_count: int, file_contents: list[bytes]) -> None:
    """
    Arka planda çalışan rapor pipeline.

    BackgroundTasks ile çağrılır — kendi DB session'ını açar/kapatır.

    Args:
        job_id:        ReportJob.id (string UUID)
        file_count:    Yüklenen dosya sayısı
        file_contents: Her dosyanın ham bytes içeriği
    """
    db = SessionLocal()
    try:
        logger.info("Pipeline başladı — job=%s, dosya=%d", job_id, file_count)

        # ── 1. PDF Parse ───────────────────────────────────────────────────
        filenames = [f"upload_{i+1}.pdf" for i in range(len(file_contents))]
        try:
            parsed_results = parse_uploaded_files(file_contents, filenames)
        except ParsePipelineError as exc:
            logger.error("Pipeline — parse tamamen başarısız: %s", exc)
            report_job_repo.update_status(
                db, job_id, "failed",
                extra={"error": f"PDF parse edilemedi: {exc}"},
            )
            return

        logger.info(
            "Pipeline — parse tamamlandı: %d/%d PDF başarılı",
            len(parsed_results), file_count,
        )

        # ── 1b. Parse kalite kontrolü ──────────────────────────────────────
        # Geçerli rapor için: gerçek öğrenci adı + en az 1 ders neti zorunlu.
        _UNKNOWN_NAMES = frozenset({
            "Bilinmeyen Öğrenci", "", "Öğrenci", "Student", "Test",
            "Öğrenci Adı", "Ad Soyad", "OGRENCI",
        })
        has_real_name = any(
            (r.student_name or "").strip() not in _UNKNOWN_NAMES
            for r in parsed_results
        )
        has_subjects = any(len(r.subjects) > 0 for r in parsed_results)

        if not has_real_name or not has_subjects:
            missing = []
            if not has_real_name:
                missing.append("öğrenci adı")
            if not has_subjects:
                missing.append("ders netleri")
            error_msg = (
                f"Parse kalitesi yetersiz: {' ve '.join(missing)} çıkarılamadı. "
                "PDF formatı desteklenmiyor olabilir; "
                "debug için: python scripts/test_parser.py --input <dosya.pdf>"
            )
            logger.error("Pipeline — parse kalite hatası: %s", error_msg)
            report_job_repo.update_status(
                db, job_id, "failed",
                extra={"error": error_msg},
            )
            return

        # ── 2. NormalizedExamResult → exam dict ────────────────────────────
        exams = [normalized_to_exam_dict(r) for r in parsed_results]
        logger.info("Pipeline — %d sınav verisi dönüştürüldü", len(exams))

        # ── 3. Öğrenci kimliği ─────────────────────────────────────────────
        student_name, grade = resolve_student_identity(parsed_results)
        logger.info("Pipeline — öğrenci: %r, sınıf: %r", student_name, grade)

        # ── 4. student_data oluştur ────────────────────────────────────────
        student_data = build_student_data(
            name=student_name,
            grade=grade,
            exams=exams,
        )

        # Kısmi parse varsa tier uyarısına not düş
        if len(parsed_results) < file_count:
            partial_note = (
                f"{file_count - len(parsed_results)} PDF parse edilemedi; "
                f"{len(parsed_results)} dosyayla rapor üretildi."
            )
            tier = student_data.get("analysis_tier", {})
            existing_warning = tier.get("warning") or ""
            tier["warning"] = (partial_note + " " + existing_warning).strip()
            student_data["analysis_tier"] = tier

        # ── 5. Grafikler ───────────────────────────────────────────────────
        output_path = settings.output_dir / f"{job_id}.docx"
        charts_dir  = settings.output_dir / f"{job_id}_charts"
        generate_all_charts(student_data, charts_dir)

        # ── 6. DOCX üret ──────────────────────────────────────────────────
        generate_report(student_data, output_path, charts_dir)
        logger.info("Pipeline tamamlandı — job=%s, dosya=%s", job_id, output_path)

        # ── 7. Kimlik eşleştirme ───────────────────────────────────────────
        # Fuzzy matching ile mevcut Student kaydını bul veya yeni oluştur.
        # Eşik: 92 (token_sort_ratio). Eşleşme bulunamazsa yeni kayıt açılır.
        matched_student, created = student_repo.get_or_create_with_matching(
            db, name=student_name, grade=grade
        )
        logger.info(
            "Pipeline — öğrenci eşleme: %r (%s), created=%s",
            matched_student.name, str(matched_student.id)[:8], created,
        )

        # ── 8. Job tamamlandı ──────────────────────────────────────────────
        publishers = list({
            r.publisher for r in parsed_results if r.publisher
        })
        report_job_repo.update_status(
            db, job_id, "completed",
            extra={
                "student_id":      matched_student.id,
                "exam_count":      len(exams),
                "student_name":    student_name,
                "student_grade":   grade,
                "avg_puan":        student_data.get("avg_puan"),
                "risk_level":      student_data.get("risk", {}).get("level"),
                "trend_direction": student_data.get("trend", {}).get("direction"),
                "publishers":      publishers if publishers else None,
                "dashboard_data":  student_data,
            },
        )

    except Exception as exc:
        logger.error("Pipeline beklenmeyen hata — job=%s: %s", job_id, exc, exc_info=True)
        report_job_repo.update_status(
            db, job_id, "failed",
            extra={"error": str(exc)},
        )
    finally:
        db.close()
