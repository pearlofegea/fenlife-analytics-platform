"""initial_schema

Revision ID: 9eca1fbd541a
Revises:
Create Date: 2026-04-22

6 tablo: students, report_jobs, exams, subject_results, kazanim_results, generated_reports
"""
from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "9eca1fbd541a"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "students",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("tc_no", sa.String(11), nullable=True),
        sa.Column("grade", sa.String(20), nullable=False),
        sa.Column(
            "institution",
            sa.String(100),
            nullable=False,
            server_default="FENlife Maltepe",
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.UniqueConstraint("tc_no", name="uq_students_tc_no"),
    )

    op.create_table(
        "report_jobs",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "status",
            sa.String(20),
            nullable=False,
            server_default="processing",
        ),
        sa.Column("file_count", sa.Integer(), nullable=False),
        sa.Column(
            "student_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("students.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column("student_name", sa.String(255), nullable=True),
        sa.Column("student_grade", sa.String(20), nullable=True),
        sa.Column("exam_count", sa.Integer(), nullable=True),
        sa.Column("publishers", sa.JSON(), nullable=True),
        sa.Column("avg_puan", sa.Float(), nullable=True),
        sa.Column("risk_level", sa.String(20), nullable=True),
        sa.Column("trend_direction", sa.String(10), nullable=True),
        sa.Column("error", sa.Text(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
    )
    op.create_index("ix_report_jobs_status", "report_jobs", ["status"])
    op.create_index("ix_report_jobs_student_id", "report_jobs", ["student_id"])

    op.create_table(
        "exams",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "student_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("students.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "job_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("report_jobs.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("publisher", sa.String(50), nullable=False),
        sa.Column("exam_name", sa.String(255), nullable=False),
        sa.Column("exam_date", sa.String(10), nullable=False),
        sa.Column("total_score", sa.Float(), nullable=False),
        sa.Column("institution_avg", sa.Float(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
    )
    op.create_index("ix_exams_student_id", "exams", ["student_id"])
    op.create_index("ix_exams_exam_date", "exams", ["exam_date"])

    op.create_table(
        "subject_results",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "exam_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("exams.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("subject", sa.String(50), nullable=False),
        sa.Column("correct", sa.Integer(), nullable=False),
        sa.Column("wrong", sa.Integer(), nullable=False),
        sa.Column("blank", sa.Integer(), nullable=False),
        sa.Column("net", sa.Float(), nullable=False),
    )
    op.create_index("ix_subject_results_exam_id", "subject_results", ["exam_id"])

    op.create_table(
        "kazanim_results",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "exam_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("exams.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("subject", sa.String(50), nullable=False),
        sa.Column("kazanim_name", sa.String(500), nullable=False),
        sa.Column("kazanim_code", sa.String(50), nullable=True),
        sa.Column("total_questions", sa.Integer(), nullable=False),
        sa.Column("correct", sa.Integer(), nullable=False),
        sa.Column("wrong", sa.Integer(), nullable=False),
        sa.Column("blank", sa.Integer(), nullable=False),
        sa.Column("success_pct", sa.Float(), nullable=False),
        sa.Column("priority_pct", sa.Float(), nullable=True),
    )
    op.create_index("ix_kazanim_results_exam_id", "kazanim_results", ["exam_id"])

    op.create_table(
        "generated_reports",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "job_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("report_jobs.id", ondelete="CASCADE"),
            nullable=False,
            unique=True,
        ),
        sa.Column(
            "student_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("students.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("file_path", sa.Text(), nullable=False),
        sa.Column("docx_filename", sa.String(255), nullable=False),
        sa.Column("file_size_bytes", sa.Integer(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
    )


def downgrade() -> None:
    op.drop_table("generated_reports")
    op.drop_table("kazanim_results")
    op.drop_table("subject_results")
    op.drop_table("exams")
    op.drop_table("report_jobs")
    op.drop_table("students")
