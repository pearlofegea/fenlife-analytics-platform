"""SQLAlchemy ORM modelleri — PostgreSQL-first.

Tablo ilişkileri:
    students ──(1:N)── exams
    students ──(1:N)── report_jobs
    students ──(1:N)── generated_reports
    report_jobs ──(1:N)── exams          (job_id FK — hangi upload'dan geldi)
    report_jobs ──(1:1)── generated_reports
    exams ──(1:N)── subject_results
    exams ──(1:N)── kazanim_results
"""
import uuid
from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, Integer, JSON, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class Student(Base):
    __tablename__ = "students"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    tc_no: Mapped[str | None] = mapped_column(String(11), nullable=True, unique=True)
    grade: Mapped[str] = mapped_column(String(20), nullable=False)
    institution: Mapped[str] = mapped_column(
        String(100), nullable=False, server_default="FENlife Maltepe"
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    exams: Mapped[list["Exam"]] = relationship(
        back_populates="student", cascade="all, delete-orphan"
    )
    report_jobs: Mapped[list["ReportJob"]] = relationship(back_populates="student")
    generated_reports: Mapped[list["GeneratedReport"]] = relationship(
        back_populates="student"
    )


class ReportJob(Base):
    __tablename__ = "report_jobs"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    status: Mapped[str] = mapped_column(
        String(20), nullable=False, server_default="processing"
    )
    file_count: Mapped[int] = mapped_column(Integer(), nullable=False)
    student_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("students.id"), nullable=True
    )
    # Denormalize özet alanlar — /api/students list sorgusunda JOIN'siz hız sağlar
    student_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    student_grade: Mapped[str | None] = mapped_column(String(20), nullable=True)
    exam_count: Mapped[int | None] = mapped_column(Integer(), nullable=True)
    publishers: Mapped[list[str] | None] = mapped_column(JSON, nullable=True)
    avg_puan: Mapped[float | None] = mapped_column(Float(), nullable=True)
    risk_level: Mapped[str | None] = mapped_column(String(20), nullable=True)
    trend_direction: Mapped[str | None] = mapped_column(String(10), nullable=True)
    error: Mapped[str | None] = mapped_column(Text(), nullable=True)
    dashboard_data: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    student: Mapped["Student | None"] = relationship(back_populates="report_jobs")
    generated_report: Mapped["GeneratedReport | None"] = relationship(
        back_populates="job", uselist=False
    )

    def to_response_dict(self) -> dict:
        """API response için dict — mevcut job_store sözleşmesini korur."""
        return {
            "job_id": str(self.id),
            "status": self.status,
            "file_count": self.file_count,
            "student_name": self.student_name,
            "student_grade": self.student_grade,
            "exam_count": self.exam_count,
            "publishers": self.publishers or [],
            "avg_puan": self.avg_puan,
            "risk_level": self.risk_level,
            "trend_direction": self.trend_direction,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "download_url": (
                f"/api/reports/{self.id}/download"
                if self.status == "completed"
                else None
            ),
            "error": self.error,
        }


class Exam(Base):
    __tablename__ = "exams"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    student_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("students.id"), nullable=False
    )
    job_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("report_jobs.id"), nullable=False
    )
    publisher: Mapped[str] = mapped_column(String(50), nullable=False)
    exam_name: Mapped[str] = mapped_column(String(255), nullable=False)
    exam_date: Mapped[str] = mapped_column(String(10), nullable=False)  # "2026-02-15"
    total_score: Mapped[float] = mapped_column(Float(), nullable=False)
    institution_avg: Mapped[float | None] = mapped_column(Float(), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    student: Mapped["Student"] = relationship(back_populates="exams")
    subject_results: Mapped[list["SubjectResult"]] = relationship(
        back_populates="exam", cascade="all, delete-orphan"
    )
    kazanim_results: Mapped[list["KazanimResult"]] = relationship(
        back_populates="exam", cascade="all, delete-orphan"
    )


class SubjectResult(Base):
    __tablename__ = "subject_results"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    exam_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("exams.id"), nullable=False
    )
    subject: Mapped[str] = mapped_column(String(50), nullable=False)
    correct: Mapped[int] = mapped_column(Integer(), nullable=False)
    wrong: Mapped[int] = mapped_column(Integer(), nullable=False)
    blank: Mapped[int] = mapped_column(Integer(), nullable=False)
    net: Mapped[float] = mapped_column(Float(), nullable=False)

    exam: Mapped["Exam"] = relationship(back_populates="subject_results")


class KazanimResult(Base):
    __tablename__ = "kazanim_results"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    exam_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("exams.id"), nullable=False
    )
    subject: Mapped[str] = mapped_column(String(50), nullable=False)
    kazanim_name: Mapped[str] = mapped_column(String(500), nullable=False)
    kazanim_code: Mapped[str | None] = mapped_column(String(50), nullable=True)
    total_questions: Mapped[int] = mapped_column(Integer(), nullable=False)
    correct: Mapped[int] = mapped_column(Integer(), nullable=False)
    wrong: Mapped[int] = mapped_column(Integer(), nullable=False)
    blank: Mapped[int] = mapped_column(Integer(), nullable=False)
    success_pct: Mapped[float] = mapped_column(Float(), nullable=False)
    priority_pct: Mapped[float | None] = mapped_column(Float(), nullable=True)

    exam: Mapped["Exam"] = relationship(back_populates="kazanim_results")


class GeneratedReport(Base):
    __tablename__ = "generated_reports"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    job_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("report_jobs.id"), nullable=False, unique=True
    )
    student_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("students.id"), nullable=False
    )
    file_path: Mapped[str] = mapped_column(Text(), nullable=False)
    docx_filename: Mapped[str] = mapped_column(String(255), nullable=False)
    file_size_bytes: Mapped[int | None] = mapped_column(Integer(), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    job: Mapped["ReportJob"] = relationship(back_populates="generated_report")
    student: Mapped["Student"] = relationship(back_populates="generated_reports")
