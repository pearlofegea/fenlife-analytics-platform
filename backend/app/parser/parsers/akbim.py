"""AKBİM PDF adaptörü — örnek publisher-specific adapter.

Bu adaptör GenericPDFAdapter'ın üzerine AKBİM formatına özgü
çıkarımlar ekler. GenericPDFAdapter çalıştıktan sonra devreye girer.

TODO Sprint 2B:
- pymupdf ile AKBİM deneme tablosu çıkarımı
- Öncelikli kazanımlar tablosu (ilk 50 kazanım)
- Zorluk analizi tablosu (Çok Zor/Zor/Orta/Kolay/Çok Kolay)
"""
from pathlib import Path

from app.parser.parsers.base import BaseAdapter
from app.parser.schemas import NormalizedExamResult


class AKBIMAdapter(BaseAdapter):
    source_type = "pdf_akbim"

    def parse(self, pdf_path: Path) -> NormalizedExamResult:
        raise NotImplementedError("Sprint 2B'de implementasyon gelecek")
