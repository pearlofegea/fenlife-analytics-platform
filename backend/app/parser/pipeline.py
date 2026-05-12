"""
PDF upload pipeline — bytes → NormalizedExamResult listesi.

Akış:
  1. Her PDF bytes için yayıncıyı tespit et (detect_publisher_from_bytes).
  2. Yayıncıya özel adaptör varsa onu kullan; yoksa GenericPDFAdapter dene.
  3. Her dosya bağımsız parse edilir — biri başarısız olursa diğerleri etkilenmez.
  4. En az bir sonuç varsa devam edilir; tümü başarısızsa ParsePipelineError fırlatılır.

Döndürülen exam dict formatı (analytics.build_student_data uyumlu):
  {date, name, publisher, turkce, matematik, fen, sosyal, din, ydil, puan}
"""
import logging
from dataclasses import dataclass

from app.parser.detector import Publisher, detect_publisher_from_bytes
from app.parser.parsers.generic import GenericPDFAdapter, ParseError
from app.parser.schemas import NormalizedExamResult

logger = logging.getLogger(__name__)

_generic_adapter = GenericPDFAdapter()


class ParsePipelineError(Exception):
    """Hiçbir PDF parse edilemedi."""


@dataclass
class ParseResult:
    filename: str
    success: bool
    result: NormalizedExamResult | None = None
    error: str | None = None


def _get_adapter(publisher: Publisher):
    """
    Yayıncıya özel adaptör döndür.
    Özel adaptörler henüz implementte edilmediğinden (Sprint 2B TODO),
    tümü şimdilik GenericPDFAdapter'a düşüyor.
    """
    # Sprint 2B'de buraya AKBIMAdapter(), TODERAdapter() vs eklenecek:
    # if publisher == Publisher.AKBIM: return AKBIMAdapter()
    return _generic_adapter


def parse_uploaded_files(
    file_contents: list[bytes],
    filenames: list[str] | None = None,
) -> list[NormalizedExamResult]:
    """
    Yüklenen PDF bytes listesini parse eder.

    Args:
        file_contents: Her PDF'in ham bytes içeriği
        filenames: Opsiyonel dosya adları (loglama ve raw_source_ref için)

    Returns:
        Başarıyla parse edilen NormalizedExamResult listesi

    Raises:
        ParsePipelineError: Hiçbir dosya parse edilemediyse
    """
    if not file_contents:
        raise ParsePipelineError("Parse edilecek dosya yok")

    names = filenames or [f"upload_{i+1}.pdf" for i in range(len(file_contents))]
    parse_results: list[ParseResult] = []

    for content, fname in zip(file_contents, names):
        logger.info("[Pipeline] Parse başlıyor — %s (%d bytes)", fname, len(content))

        publisher = detect_publisher_from_bytes(content)
        logger.info("[Pipeline] %s → yayıncı tespit: %s", fname, publisher.value)

        adapter = _get_adapter(publisher)

        try:
            norm = adapter.parse_bytes(content, filename=fname)
            # Yayıncı bilgisi tespit edildiyse NormalizedExamResult'a yaz
            if publisher != Publisher.UNKNOWN and norm.publisher is None:
                norm = norm.model_copy(update={"publisher": publisher.value.upper()})
            parse_results.append(ParseResult(filename=fname, success=True, result=norm))
            logger.info("[Pipeline] %s → parse BAŞARILI (öğrenci=%r, ders=%d)", fname, norm.student_name, len(norm.subjects))
        except ParseError as exc:
            logger.warning("[Pipeline] %s → parse BAŞARISIZ: %s", fname, exc)
            parse_results.append(ParseResult(filename=fname, success=False, error=str(exc)))
        except Exception as exc:
            logger.error("[Pipeline] %s → beklenmeyen hata: %s", fname, exc, exc_info=True)
            parse_results.append(ParseResult(filename=fname, success=False, error=str(exc)))

    successes = [r.result for r in parse_results if r.success and r.result]
    failures = [r for r in parse_results if not r.success]

    if failures:
        logger.warning(
            "[Pipeline] %d/%d dosya parse edilemedi: %s",
            len(failures),
            len(parse_results),
            "; ".join(f"{r.filename}: {r.error}" for r in failures),
        )

    if not successes:
        errors = "; ".join(f"{r.filename}: {r.error}" for r in failures)
        raise ParsePipelineError(
            f"Hiçbir PDF parse edilemedi ({len(failures)} dosya). Hatalar: {errors}"
        )

    logger.info("[Pipeline] Tamamlandı — %d/%d başarılı", len(successes), len(parse_results))
    return successes


def normalized_to_exam_dict(norm: NormalizedExamResult) -> dict:
    """
    NormalizedExamResult → analytics.build_student_data'nın beklediği dict.
    """
    subjects = {s.subject: s.net for s in norm.subjects}
    return {
        "date":      norm.exam_date.isoformat(),
        "name":      norm.exam_name,
        "publisher": norm.publisher or norm.source_type,
        "turkce":    subjects.get("turkce",    0.0),
        "matematik": subjects.get("matematik", 0.0),
        "fen":       subjects.get("fen",       0.0),
        "sosyal":    subjects.get("sosyal",    0.0),
        "din":       subjects.get("din",       0.0),
        "ydil":      subjects.get("ydil",      0.0),
        "puan":      norm.total_score,
    }


def resolve_student_identity(results: list[NormalizedExamResult]) -> tuple[str, str]:
    """
    Parse sonuçlarından öğrenci adı ve sınıf belirle.

    Strateji: En uzun (en bilgili) adı taşıyan sonucu al.
    Sprint 2C'de IdentityResolver bunu devralacak.
    """
    # Ad ve sınıf için en iyi kaynağı bul
    best_name = "Bilinmeyen Öğrenci"
    best_grade = "8"

    for norm in results:
        name = (norm.student_name or "").strip()
        if name and name != "Bilinmeyen Öğrenci":
            # En uzun gerçek adı seç; best_name hâlâ default ise ilk gerçek adı kabul et
            if best_name == "Bilinmeyen Öğrenci" or len(name) > len(best_name):
                best_name = name
        if norm.grade and norm.grade != "8":
            best_grade = norm.grade

    return best_name, best_grade
