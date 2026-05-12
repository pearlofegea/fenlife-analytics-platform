"""
DEPRECATED — Sprint 1.5'te yerini app/repositories/report_job_repo.py aldı.

Bu dosya referans amaçlı korunmaktadır. Aktif route'lar artık bu modülü
kullanmıyor; Sprint 2 tamamlandıktan sonra silinebilir.
"""
import json
from datetime import datetime
from pathlib import Path
from typing import Any

from app.config import settings

# In-memory store: job_id → dict
_jobs: dict[str, dict] = {}


def _sidecar_path(job_id: str) -> Path:
    return settings.output_dir / f"{job_id}.json"


def _load_from_disk(job_id: str) -> dict | None:
    path = _sidecar_path(job_id)
    if path.exists():
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            return None
    return None


def save(job_id: str, data: dict) -> None:
    """Job state'i hem memory'e hem diske yaz."""
    _jobs[job_id] = data
    try:
        settings.output_dir.mkdir(parents=True, exist_ok=True)
        _sidecar_path(job_id).write_text(
            json.dumps(data, ensure_ascii=False, default=str, indent=2),
            encoding="utf-8",
        )
    except Exception:
        pass  # disk yazımı başarısız olsa da in-memory çalışmaya devam eder


def get(job_id: str) -> dict | None:
    """Job state'i getir — önce memory, sonra disk."""
    if job_id in _jobs:
        return _jobs[job_id]
    data = _load_from_disk(job_id)
    if data:
        _jobs[job_id] = data
    return data


def update_status(job_id: str, status: str, extra: dict[str, Any] | None = None) -> None:
    """Sadece status alanını güncelle."""
    job = get(job_id) or {}
    job["status"] = status
    job["updated_at"] = datetime.utcnow().isoformat()
    if extra:
        job.update(extra)
    save(job_id, job)


def create(job_id: str, file_count: int) -> dict:
    """Yeni job kaydı oluştur, 'processing' statüsüyle başlat."""
    data: dict[str, Any] = {
        "job_id": job_id,
        "status": "processing",
        "file_count": file_count,
        "created_at": datetime.utcnow().isoformat(),
        "updated_at": datetime.utcnow().isoformat(),
        "student_name": None,
        "student_grade": None,
        "exam_count": None,
        "publishers": [],
        "avg_puan": None,
        "risk_level": None,
        "trend_direction": None,
        "download_url": None,
        "error": None,
    }
    save(job_id, data)
    return data
