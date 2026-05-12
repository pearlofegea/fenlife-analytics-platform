"""TÖDER PDF adaptörü — örnek publisher-specific adapter. TODO Sprint 2B."""
from pathlib import Path

from app.parser.parsers.base import BaseAdapter
from app.parser.schemas import NormalizedExamResult


class TODERAdapter(BaseAdapter):
    source_type = "pdf_toder"

    def parse(self, pdf_path: Path) -> NormalizedExamResult:
        raise NotImplementedError("Sprint 2B'de implementasyon gelecek")
