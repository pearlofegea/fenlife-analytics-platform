"""Tüm input adaptörleri için soyut temel sınıf.

Mimari: Input Adapters → NormalizedExamResult → Analysis Engine
Her adaptör (AKBIM, TÖDER, GenericPDF vs.) bu sınıftan türetilir.
"""
from abc import ABC, abstractmethod
from pathlib import Path

from app.parser.schemas import NormalizedExamResult


class BaseAdapter(ABC):
    """Herhangi bir PDF kaynağını NormalizedExamResult'a dönüştürür."""

    source_type: str = "unknown"

    @abstractmethod
    def parse(self, pdf_path: Path) -> NormalizedExamResult:
        """PDF'i parse et, normalize edilmiş sonuç döndür."""
        ...
