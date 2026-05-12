"""Rapor endpoint'leri.

Akış:
  POST /api/reports          → PDF yükle, job başlat
  GET  /api/reports/{job_id} → job durumunu sorgula
  GET  /api/reports/{job_id}/download → DOCX indir
"""
from typing import Annotated
from uuid import uuid4

from fastapi import APIRouter, BackgroundTasks, Depends, File, HTTPException, UploadFile
from fastapi.responses import FileResponse, JSONResponse
from sqlalchemy.orm import Session

from app.config import settings
from app.db.session import get_db
from app.repositories import report_job_repo
from app.services.report_service import run_pipeline

router = APIRouter()


@router.post("/reports", status_code=202)
async def create_report(
    background_tasks: BackgroundTasks,
    files: Annotated[list[UploadFile], File(description="Sınav sonucu PDF dosyaları")],
    db: Session = Depends(get_db),
):
    """
    Sınav PDF'leri yükle, rapor üretimini başlat.

    Tek dosya da kabul edilir. Daha güvenilir analiz için en az
    {recommended_exam_count} sınav verisi önerilir; aksi hâlde yanıtta
    'data_warning' alanı doldurulur.

    Returns 202 Accepted:
        {
            "job_id": "uuid",
            "status": "processing",
            "file_count": N,
            "data_warning": str | null,
            "message": "..."
        }
    """
    if len(files) < settings.min_exam_count:
        raise HTTPException(
            status_code=400,
            detail="En az 1 PDF dosyası gönderilmelidir.",
        )

    job_id = str(uuid4())
    job = report_job_repo.create(db, job_id=job_id, file_count=len(files))

    data_warning: str | None = None
    if len(files) < settings.recommended_exam_count:
        data_warning = (
            f"{len(files)} dosya yüklendi. Daha güvenilir analiz, gelişim takibi "
            f"ve eğilim yorumları için en az {settings.recommended_exam_count} sınav "
            f"verisi önerilir. Az veriyle de rapor oluşturulabilir; ancak "
            f"karşılaştırmalı içgörüler sınırlı kalabilir."
        )

    # Dosya içeriklerini request context kapanmadan oku (BackgroundTask bunu göremez)
    file_contents = [await f.read() for f in files]

    background_tasks.add_task(run_pipeline, job_id, len(files), file_contents)

    return JSONResponse(
        status_code=202,
        content={
            "job_id": str(job.id),
            "status": job.status,
            "file_count": job.file_count,
            "data_warning": data_warning,
            "message": "İş kuyruğa alındı. Parser modülü Sprint 2'de bağlanacak.",
        },
    )


@router.get("/reports/{job_id}")
async def get_report_status(job_id: str, db: Session = Depends(get_db)):
    """
    Job durumunu sorgula.

    Returns:
        {
            "job_id": str,
            "status": "processing" | "completed" | "failed",
            "student_name": str | null,
            ...
        }
    """
    job = report_job_repo.get(db, job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="Job bulunamadı")
    return job.to_response_dict()


@router.get("/reports/{job_id}/download")
async def download_report(job_id: str, db: Session = Depends(get_db)):
    """Oluşturulan DOCX raporunu indir."""
    job = report_job_repo.get(db, job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="Job bulunamadı")
    if job.status != "completed":
        raise HTTPException(
            status_code=409,
            detail=f"Rapor henüz hazır değil. Durum: {job.status}",
        )

    report_path = settings.output_dir / f"{job_id}.docx"
    if not report_path.exists():
        raise HTTPException(status_code=404, detail="DOCX dosyası bulunamadı")

    student_slug = (job.student_name or job_id[:8]).replace(" ", "_").lower()
    return FileResponse(
        path=report_path,
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        filename=f"fenlife_rapor_{student_slug}.docx",
    )
