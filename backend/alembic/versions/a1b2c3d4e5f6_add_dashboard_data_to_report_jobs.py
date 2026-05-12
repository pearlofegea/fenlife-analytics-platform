"""add_dashboard_data_to_report_jobs

Revision ID: a1b2c3d4e5f6
Revises: 9eca1fbd541a
Create Date: 2026-04-25

report_jobs tablosuna dashboard_data JSON kolonu ekler.
Pipeline tamamlanınca tam student_data dict burada saklanır.
Dashboard endpoint bu kolonu döner.
"""
from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "a1b2c3d4e5f6"
down_revision: Union[str, None] = "9eca1fbd541a"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "report_jobs",
        sa.Column("dashboard_data", sa.JSON(), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("report_jobs", "dashboard_data")
