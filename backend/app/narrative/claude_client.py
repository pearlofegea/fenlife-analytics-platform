"""
Claude API wrapper — 7 bölümlü rapor metni üretimi.

Feature'ları alır, Claude'a gönderir, 7 bölüm için akıcı Türkçe metin döndürür.
"""
from anthropic import Anthropic

from app.config import settings


class ClaudeNarrator:
    def __init__(self):
        self.client = Anthropic(api_key=settings.anthropic_api_key)

    def generate_narrative(self, features: dict) -> dict:
        """
        Feature dict'inden 7 bölümlü narrative üret.

        Returns:
            {
                "ogrenci_ozeti": str,
                "kritik_bulgular": list[str],
                "ders_analizi": str,
                "brans_aksiyonlari": list[dict],
                "rehberlik_aksiyonlari": list[dict],
                "calisma_kagidi_girdileri": list[dict],
                "takip_hedefleri": list[dict],
            }
        """
        raise NotImplementedError("Sprint 5'te implementasyon gelecek")
