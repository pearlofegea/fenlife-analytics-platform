"""
PDF yayıncı tespiti.

İlk 250-300 karakteri okuyarak hangi yayıncının formatı olduğunu
belirler ve uygun parser'a yönlendirir.

Framework'teki kararlardan:
- pymupdf (fitz) page.get_text() ile ilk 300 char oku
- XML placeholder değil, keyword tabanlı eşleştirme
"""
from enum import Enum
from pathlib import Path

import pymupdf  # fitz


class Publisher(str, Enum):
    AKBIM = "akbim"
    TODER = "toder"
    NARTEST = "nartest"
    FINAL = "final"
    MOZAIK = "mozaik"
    PARAF = "paraf"
    NEWTON = "newton"
    FENOMEN = "fenomen"
    UNKNOWN = "unknown"


PUBLISHER_SIGNATURES = {
    Publisher.AKBIM: ["AKBİM", "final kurs merkezleri"],
    Publisher.TODER: ["TÖDER", "TODER"],
    Publisher.NARTEST: ["NARTEST", "NAR TEST", "NARTest"],
    Publisher.FINAL: ["FİNAL YAYINLARI", "FINAL TÜRKİYE GENELİ"],
    Publisher.MOZAIK: ["MOZAİK", "Mozaik Yayınları"],
    Publisher.PARAF: ["PARAF"],
    Publisher.NEWTON: ["NEWTON"],
    Publisher.FENOMEN: ["FENOMEN"],
}


def detect_publisher(pdf_path: Path, probe_chars: int = 300) -> Publisher:
    """PDF dosya yolundan yayıncıyı tespit eder."""
    with pymupdf.open(pdf_path) as doc:
        if len(doc) == 0:
            return Publisher.UNKNOWN
        first_page_text = doc[0].get_text()[:probe_chars].upper()
        for publisher, signatures in PUBLISHER_SIGNATURES.items():
            for sig in signatures:
                if sig.upper() in first_page_text:
                    return publisher
    return Publisher.UNKNOWN


def detect_publisher_from_bytes(content: bytes, probe_chars: int = 300) -> Publisher:
    """Ham PDF bytes'tan yayıncıyı tespit eder (upload akışı için)."""
    try:
        with pymupdf.open(stream=content, filetype="pdf") as doc:
            if len(doc) == 0:
                return Publisher.UNKNOWN
            first_page_text = doc[0].get_text()[:probe_chars].upper()
            for publisher, signatures in PUBLISHER_SIGNATURES.items():
                for sig in signatures:
                    if sig.upper() in first_page_text:
                        return publisher
    except Exception:
        return Publisher.UNKNOWN
    return Publisher.UNKNOWN
