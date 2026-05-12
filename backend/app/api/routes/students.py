"""Öğrenci endpoint'leri.

GET /api/students                        → tüm öğrencileri listele (DB)
GET /api/students/{student_id}           → öğrenci detayı (job_id ile aranır)
GET /api/students/{student_id}/dashboard → dashboard verisi (student_data JSON)

Not: {student_id} parametresi aslında ReportJob.id (job_id) ile eşleştirilir.
     Student.id değil — frontend job_id gönderir, backend job_id kabul eder.
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.models import ReportJob
from app.db.session import get_db
from app.repositories import report_job_repo
from app.report.learning_outcomes import generate_estimated_topics

router = APIRouter()

_RISK_LABELS: dict[str, str] = {
    "dusuk":   "Düşük Risk",
    "orta":    "Orta Risk",
    "yuksek":  "Yüksek Risk",
    "sinirli": "Sınırlı Analiz",
}


def _build_minimal_dashboard(job: ReportJob) -> dict:
    """
    dashboard_data olmayan eski job'lar için özet alanlardan minimal dict üretir.
    exams listesi boş gelir; frontend buna göre sınırlı görünüm sunar.
    """
    level = job.risk_level or "sinirli"
    return {
        "name":         job.student_name or "—",
        "grade":        job.student_grade or "—",
        "avg_puan":     float(job.avg_puan or 0.0),
        "exams":        [],
        "subject_avgs": [],
        "priority_topics": [],
        "difficulty":   {},
        "worst_gap":    None,
        "risk": {
            "level": level,
            "label": _RISK_LABELS.get(level, "Sınırlı Analiz"),
        },
        "trend": {
            "slope":     0.0,
            "delta":     0.0,
            "direction": job.trend_direction or "flat",
        },
        "analysis_tier": {
            "level":   "limited",
            "label":   "Sınırlı Veri",
            "warning": (
                "Bu rapor eski sürümle oluşturulmuş — sınav detayları mevcut değil. "
                "Tam grafik ve ders bazlı analiz için PDF'leri yeniden yükleyin."
            ),
        },
    }


@router.get("/students")
async def list_students(db: Session = Depends(get_db)):
    """Tamamlanmış job'lardan öğrenci özetlerini döndür."""
    jobs = report_job_repo.get_all_completed(db)
    return {
        "students": [
            {
                "job_id":           str(job.id),
                "student_name":     job.student_name,
                "student_grade":    job.student_grade,
                "avg_puan":         job.avg_puan,
                "risk_level":       job.risk_level,
                "trend_direction":  job.trend_direction,
                "exam_count":       job.exam_count,
                "created_at":       job.created_at.isoformat() if job.created_at else None,
            }
            for job in jobs
        ]
    }


@router.get("/students/{student_id}")
async def get_student(student_id: str, db: Session = Depends(get_db)):
    """Tek öğrenci detayını getir (job_id ile aranır)."""
    job = report_job_repo.get(db, student_id)
    if job is None:
        raise HTTPException(status_code=404, detail="Öğrenci bulunamadı")
    return job.to_response_dict()


@router.get("/students/{student_id}/dashboard")
async def get_student_dashboard(student_id: str, db: Session = Depends(get_db)):
    """
    Dashboard için tam veri seti — student_data JSON'u döner.

    - dashboard_data varsa → doğrudan döner.
    - dashboard_data yoksa → job özet alanlarından minimal fallback üretir (404 vermez).
    - Her iki durumda da priority_topics boşsa tahmini kazanım önerileri eklenir.
    """
    job = report_job_repo.get(db, student_id)
    if job is None:
        raise HTTPException(status_code=404, detail="Öğrenci bulunamadı")
    if job.status != "completed":
        raise HTTPException(
            status_code=409,
            detail=f"Analiz henüz tamamlanmadı. Durum: {job.status}",
        )

    # Gerçek veri varsa kullan; yoksa özet alanlardan minimal dashboard üret
    if job.dashboard_data:
        data = dict(job.dashboard_data)
    else:
        data = _build_minimal_dashboard(job)

    # priority_topics boşsa tahmini konu önerileri ekle
    if not data.get("priority_topics"):
        estimated = generate_estimated_topics(
            exams=data.get("exams", []),
            subject_avgs=data.get("subject_avgs") or None,
        )
        if estimated:
            data["priority_topics"] = estimated

    return data
