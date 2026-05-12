"""Sınav sonucu Pydantic şemaları — kaynak bağımsız ortak format.

Mimari: Input Adapters → NormalizedExamResult → Analysis Engine → Output
Herhangi bir kaynaktan (PDF, CSV, manuel) gelen veri bu şemaya map edilir.
"""
from datetime import date
from typing import Literal

from pydantic import BaseModel


class SubjectResult(BaseModel):
    """Tek bir dersin net sonucu."""
    subject: str            # "turkce", "matematik", "fen", "sosyal", "din", "ydil"
    correct: int
    wrong: int
    blank: int
    net: float


class KazanimBreakdown(BaseModel):
    """Kazanım bazlı kırılım — opsiyonel, her kaynak sağlamayabilir."""
    subject: str
    kazanim_name: str
    kazanim_code: str | None = None
    total_questions: int
    correct: int
    wrong: int
    blank: int
    success_pct: float
    priority_pct: float | None = None


SourceType = Literal[
    "pdf_generic",    # herhangi bir PDF — GenericPDFAdapter
    "pdf_akbim",      # AKBIM formatı — AKBIMAdapter
    "pdf_toder",      # TÖDER formatı — TODERAdapter
    "pdf_nartest",    # Nartest formatı — NartestAdapter
    "manual",         # manuel giriş (ilerisi)
    "csv",            # CSV import (ilerisi)
    "unknown",        # tespit edilemeyen format
]


class NormalizedExamResult(BaseModel):
    """Herhangi bir kaynaktan gelen sınav sonucunun ortak şeması.

    Tüm input adaptörleri bu şemaya çıkar. Analysis Engine yalnızca
    bu şemayı tüketir — kaynak formattan habersizdir.
    """
    # Öğrenci
    student_name: str
    grade: str | None = None          # "8-01"
    institution: str | None = None

    # Sınav meta
    exam_name: str
    exam_date: date
    source_type: SourceType = "unknown"
    publisher: str | None = None       # opsiyonel — "AKBIM", "TÖDER" vs.
    raw_source_ref: str | None = None  # dosya adı — audit/debug için

    # Puanlama
    total_score: float
    institution_avg: float | None = None

    # Ders bazlı (zorunlu — minimum analiz için gerekli)
    subjects: list[SubjectResult]

    # Kazanım kırılımı (opsiyonel)
    kazanim_breakdown: list[KazanimBreakdown] = []
