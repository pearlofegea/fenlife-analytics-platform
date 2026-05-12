"""ReportJob veri erişim katmanı — job_store.py'ın DB karşılığı.

job_store.py'ın tüm public fonksiyonları burada karşılanır:
    create()        → report_job_repo.create()
    get()           → report_job_repo.get()
    update_status() → report_job_repo.update_status()
"""
from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any

from sqlalchemy.orm import Session

from app.db.models import ReportJob


def create(db: Session, job_id: str, file_count: int) -> ReportJob:
    """Yeni job kaydı oluştur, 'processing' statüsüyle başlat."""
    job = ReportJob(
        id=uuid.UUID(job_id),
        status="processing",
        file_count=file_count,
    )
    db.add(job)
    db.commit()
    db.refresh(job)
    return job


def get(db: Session, job_id: str) -> ReportJob | None:
    """Job'ı ID ile getir. Geçersiz UUID formatı → None döner."""
    try:
        uid = uuid.UUID(job_id)
    except ValueError:
        return None
    return db.get(ReportJob, uid)


def update_status(
    db: Session,
    job_id: str,
    status: str,
    extra: dict[str, Any] | None = None,
) -> None:
    """Job statüsünü ve isteğe bağlı ek alanları güncelle."""
    job = get(db, job_id)
    if job is None:
        return

    job.status = status
    job.updated_at = datetime.now(timezone.utc)

    if extra:
        allowed = {
            "student_name", "student_grade", "exam_count", "publishers",
            "avg_puan", "risk_level", "trend_direction", "error", "student_id",
            "dashboard_data",
        }
        for key, value in extra.items():
            if key in allowed and hasattr(job, key):
                setattr(job, key, value)

    db.commit()


_PLACEHOLDER_NAMES = {
    "Öğrenci", "Student", "Test", "Öğrenci Adı",
    "Bilinmeyen Öğrenci", "Ad Soyad", "OGRENCI", "Ad Soyad Giriniz",
}

def get_all_completed(db: Session) -> list[ReportJob]:
    """Status'u 'completed' olan gerçek öğrenci job'larını döndür.

    Filtreler:
    - student_name boş veya None olanlar çıkar
    - Bilinen placeholder isimler çıkar
    - exam_count 0 veya None olanlar çıkar (veri olmayan test job'ları)
    """
    jobs = (
        db.query(ReportJob)
        .filter(
            ReportJob.status == "completed",
            ReportJob.student_name.isnot(None),
            ReportJob.student_name != "",
            ReportJob.exam_count.isnot(None),
            ReportJob.exam_count > 0,
        )
        .order_by(ReportJob.created_at.desc())
        .all()
    )
    return [j for j in jobs if j.student_name not in _PLACEHOLDER_NAMES]
