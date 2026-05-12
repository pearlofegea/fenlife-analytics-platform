"""
PDF parse debug aracı — ham metin + tüm parse sonuçlarını gösterir.

Kullanım:
    python scripts/test_parser.py --input path/to/pdf
    python scripts/test_parser.py --input path/to/pdf --text-chars 3000
    python scripts/test_parser.py --input path/to/pdf --full-text
"""
import argparse
import sys
from pathlib import Path

import pymupdf

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.parser.detector import detect_publisher_from_bytes
from app.parser.parsers.generic import GenericPDFAdapter, ParseError
from app.parser.pipeline import normalized_to_exam_dict


_UNKNOWN_NAMES = frozenset({
    "Bilinmeyen Öğrenci", "", "Öğrenci", "Student", "Test",
    "Öğrenci Adı", "Ad Soyad", "OGRENCI",
})


def main():
    ap = argparse.ArgumentParser(description="FENlife PDF parse debug aracı")
    ap.add_argument("--input", required=True, type=Path, help="Test edilecek PDF dosyası")
    ap.add_argument("--text-chars", type=int, default=2500,
                    help="Gösterilecek ham metin uzunluğu (default: 2500)")
    ap.add_argument("--full-text", action="store_true", help="Ham metnin tamamını göster")
    args = ap.parse_args()

    if not args.input.exists():
        print(f"HATA: Dosya bulunamadı: {args.input}")
        sys.exit(1)

    content = args.input.read_bytes()
    print(f"\n{'='*60}")
    print(f"Dosya : {args.input.name}  ({len(content):,} bytes)")
    print(f"{'='*60}\n")

    # ── Yayıncı tespiti ──────────────────────────────────────────────────
    publisher = detect_publisher_from_bytes(content)
    print(f"[Tespit] Yayıncı: {publisher.value}\n")

    # ── Ham metin ────────────────────────────────────────────────────────
    try:
        doc = pymupdf.open(stream=content, filetype="pdf")
        full_text = "\n".join(page.get_text() for page in doc)
        doc.close()
    except Exception as e:
        print(f"[HATA] PDF açılamadı: {e}")
        sys.exit(1)

    print(f"[Ham Metin] Toplam: {len(full_text):,} karakter")
    print("-" * 60)
    if args.full_text:
        print(full_text)
    else:
        limit = args.text_chars
        print(full_text[:limit])
        if len(full_text) > limit:
            print(f"\n... [{len(full_text) - limit:,} karakter daha — --full-text ile tamamını gör]")
    print("-" * 60)

    # ── Parse işlemi ─────────────────────────────────────────────────────
    print("\n[Parse] Başlıyor...")
    adapter = GenericPDFAdapter()
    try:
        result = adapter.parse_bytes(content, filename=args.input.name)
    except ParseError as e:
        print(f"\n[Parse BAŞARISIZ] {e}")
        sys.exit(1)

    # ── Sonuçlar ─────────────────────────────────────────────────────────
    print(f"\n{'='*60}")
    print("PARSE SONUÇLARI")
    print(f"{'='*60}")
    print(f"  Öğrenci Adı  : {result.student_name!r}")
    print(f"  Sınıf        : {result.grade!r}")
    print(f"  Sınav Tarihi : {result.exam_date}")
    print(f"  Sınav Adı    : {result.exam_name!r}")
    print(f"  Kaynak Tip   : {result.source_type}")
    print(f"  Yayıncı      : {result.publisher!r}")
    print(f"  Toplam Puan  : {result.total_score}")
    print(f"  Ders Sayısı  : {len(result.subjects)}")

    if result.subjects:
        print("\n  DERS NETLERİ:")
        for s in result.subjects:
            print(f"    {s.subject:<12}  D:{s.correct:2d}  Y:{s.wrong:2d}  B:{s.blank:2d}  Net:{s.net:6.2f}")
    else:
        print("\n  [!] HİÇBİR DERS NETİ ÇIKARILAMADI")

    # ── Exam dict ────────────────────────────────────────────────────────
    print("\n  EXAM DICT (analytics'e gidecek):")
    exam_dict = normalized_to_exam_dict(result)
    for k, v in exam_dict.items():
        print(f"    {k:<12}: {v!r}")

    # ── Kalite değerlendirmesi ────────────────────────────────────────────
    name_ok = result.student_name not in _UNKNOWN_NAMES
    subj_ok = len(result.subjects) > 0

    print(f"\n{'='*60}")
    print("KALİTE KONTROLÜ")
    print(f"{'='*60}")
    print(f"  Ad      : {'✓ OK' if name_ok else '✗ BAŞARISIZ'} ({result.student_name!r})")
    print(f"  Dersler : {'✓ OK (' + str(len(result.subjects)) + ' ders)' if subj_ok else '✗ BAŞARISIZ (0 ders)'}")
    if name_ok and subj_ok:
        print("  Sonuç   : RAPOR ÜRETİLİR ✓")
    else:
        print("  Sonuç   : RAPOR REDDEDİLİR ✗  (quality gate devreye girer)")
        print()
        print("  Tanı için ham metindeki anahtar kelimeleri incele:")
        hints = []
        if not name_ok:
            hints.append("  - Öğrenci adı: ÖĞRENCİ, ADI SOYADI, SOYADI-ADI, Öğrenci Adı kalıplarını ara")
        if not subj_ok:
            hints.append("  - Ders netleri: TÜRKÇE, MATEMATİK gibi satırları ve yanındaki sayıları ara")
            hints.append("  - Format: 'DERS D Y B NET' mi? 'DERS SORU D Y B NET' mi? 'D:x Y:x Net:x' mi?")
        for h in hints:
            print(h)
    print(f"{'='*60}\n")


if __name__ == "__main__":
    main()
