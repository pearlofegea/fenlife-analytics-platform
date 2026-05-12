"""Rapor metadata Pydantic modeli."""
from datetime import datetime
from pydantic import BaseModel


class ReportMetadata(BaseModel):
    job_id: str
    student_id: str
    created_at: datetime
    docx_path: str
    exam_count: int
    status: str  # "pending" | "processing" | "completed" | "failed"
