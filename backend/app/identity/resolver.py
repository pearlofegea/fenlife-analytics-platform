"""Öğrenci kimlik çözümleme.

Birden fazla PDF'in aynı öğrenciye mi ait olduğunu belirler.
- TC kimlik no varsa primary key olarak kullanılır
- Yoksa rapidfuzz token_set_ratio ile isim eşleştirme
  (örn: "Mehmet Taha Baş" ↔ "Taha Baş" eşleşir)
"""
from rapidfuzz import fuzz

from app.parser.schemas import NormalizedExamResult


class IdentityResolver:
    """NormalizedExamResult listesini öğrenci bazında gruplandırır."""

    MATCH_THRESHOLD = 85  # token_set_ratio eşik

    def resolve(
        self, exams: list[NormalizedExamResult]
    ) -> dict[str, list[NormalizedExamResult]]:
        """Sınav listesini öğrenci adına göre grupla.

        Returns:
            { "normalized_name": [exam, exam, ...] }

        TODO Sprint 2C:
        - TC kimlik varsa direkt grupla
        - Yoksa fuzzy matching ile öğrenci adı normalize
        - Türkçe karakter normalize (ş→s, ğ→g için NFD ön işleme)
        """
        raise NotImplementedError("Sprint 2C'de implementasyon gelecek")

    @staticmethod
    def names_match(name_a: str, name_b: str) -> bool:
        """İki ismin aynı öğrenciye ait olup olmadığını kontrol et."""
        score = fuzz.token_set_ratio(name_a.lower(), name_b.lower())
        return score >= IdentityResolver.MATCH_THRESHOLD
