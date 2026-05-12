#!/usr/bin/env python3
"""
Demo rapor üretici — Asya Nur Tunçer için 5 deneme verisiyle DOCX rapor oluşturur.

Kullanım (proje kökünden):
    source backend/.venv/bin/activate
    python3 backend/scripts/demo_report.py

Çıktı: sample-data/demo_asya_nur_tuncer.docx
"""
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(ROOT / "backend"))

from app.report.analytics import build_student_data
from app.report.charts import generate_all_charts
from app.report.generator import generate_report

# ──────────────────────────────────────────────
# Öğrenci
# ──────────────────────────────────────────────
STUDENT_NAME = "Asya Nur Tunçer"
STUDENT_GRADE = "8-A"

# ──────────────────────────────────────────────
# 5 Deneme
# Sınav 4 (Final TÜRKİYE GENELİ DENEME1, 06.02.2026): PDF'ten gerçek veriler
# Fen: PDF'te 10 soruluk formatta 8.67 net → LGS 20 soru ölçeğine % koruyarak 17.33
# Din: kazanım breakdown toplamından hesaplanan net 6.33
# Ydil: kazanım breakdown toplamından hesaplanan net 8.67
# ──────────────────────────────────────────────
EXAMS = [
    {
        "date": "2025-11-20",
        "name": "FENlife Deneme 1",
        "publisher": "FENlife",
        "turkce":    14.33,
        "matematik": 10.67,
        "fen":       13.33,
        "sosyal":     5.67,
        "din":        5.33,
        "ydil":       6.67,
        "puan": 372,
    },
    {
        "date": "2025-12-18",
        "name": "FENlife Deneme 2",
        "publisher": "FENlife",
        "turkce":    15.67,
        "matematik": 12.00,
        "fen":       15.33,
        "sosyal":     6.33,
        "din":        6.33,
        "ydil":       7.33,
        "puan": 389,
    },
    {
        "date": "2026-01-22",
        "name": "FENlife Deneme 3",
        "publisher": "FENlife",
        "turkce":    16.00,
        "matematik": 12.67,
        "fen":       14.67,
        "sosyal":     6.67,
        "din":        6.00,
        "ydil":       8.00,
        "puan": 393,
    },
    {
        "date": "2026-02-06",
        "name": "Final TÜRKİYE GENELİ DENEME1",
        "publisher": "Final",
        "turkce":    17.33,
        "matematik": 13.67,
        "fen":       17.33,
        "sosyal":     7.33,
        "din":        6.33,
        "ydil":       8.67,
        "puan": 403,
    },
    {
        "date": "2026-03-12",
        "name": "FENlife Deneme 4",
        "publisher": "FENlife",
        "turkce":    16.67,
        "matematik": 14.00,
        "fen":       16.67,
        "sosyal":     7.67,
        "din":        7.00,
        "ydil":       8.33,
        "puan": 408,
    },
]

# ──────────────────────────────────────────────
# Öncelikli Kazanımlar
# PDF kazanım breakdown'undan düşük başarılı konular + simüle edilmiş ek konular
# ──────────────────────────────────────────────
PRIORITY_TOPICS = [
    {
        "subject": "Din Kültürü",
        "topic": "ZEKAT İBADETİ",
        "q": 2, "d": 0, "y": 2, "b": 0,
        "success": 0.0,
        "priority": 100.0,
    },
    {
        "subject": "Fen Bilimleri",
        "topic": "SIVI BASINCI",
        "q": 3, "d": 1, "y": 2, "b": 0,
        "success": 11.0,
        "priority": 89.0,
    },
    {
        "subject": "Türkçe",
        "topic": "CÜMLENİN ÖGELERİ",
        "q": 3, "d": 1, "y": 2, "b": 0,
        "success": 11.0,
        "priority": 89.0,
    },
    {
        "subject": "Fen Bilimleri",
        "topic": "PERİYODİK TABLO",
        "q": 2, "d": 1, "y": 1, "b": 0,
        "success": 33.0,
        "priority": 67.0,
    },
    {
        "subject": "Matematik",
        "topic": "ÇARPANLAR ve KATLAR",
        "q": 4, "d": 2, "y": 1, "b": 1,
        "success": 42.0,
        "priority": 58.0,
    },
    {
        "subject": "Matematik",
        "topic": "KAREKÖKLÜ SAYILAR",
        "q": 4, "d": 2, "y": 1, "b": 1,
        "success": 42.0,
        "priority": 58.0,
    },
    {
        "subject": "Matematik",
        "topic": "ÜSLÜ SAYILAR",
        "q": 7, "d": 3, "y": 0, "b": 4,
        "success": 43.0,
        "priority": 57.0,
    },
    {
        "subject": "İnkılap",
        "topic": "MİLLİ UYANIŞ",
        "q": 6, "d": 4, "y": 2, "b": 0,
        "success": 50.0,
        "priority": 50.0,
    },
    {
        "subject": "Türkçe",
        "topic": "SÖZEL MANTIK-MUHAKEME",
        "q": 2, "d": 1, "y": 1, "b": 0,
        "success": 33.0,
        "priority": 67.0,
    },
    {
        "subject": "Fen Bilimleri",
        "topic": "BİYOTEKNOLOJİ",
        "q": 2, "d": 0, "y": 1, "b": 1,
        "success": 0.0,
        "priority": 100.0,
    },
]

# ──────────────────────────────────────────────
# Zorluk Matrisi
# {ders: {q: [ÇokKolay, Kolay, Orta, Zor, ÇokZor soru sayısı],
#          sD: [öğrenci doğru], gD: [kurum doğru]}}
# ──────────────────────────────────────────────
DIFFICULTY = {
    "turkce":    {"q": [4, 5, 5, 4, 2], "sD": [4, 5, 4, 2, 0], "gD": [4, 4, 3, 2, 1]},
    "matematik": {"q": [2, 4, 6, 5, 3], "sD": [2, 3, 3, 2, 0], "gD": [2, 3, 4, 3, 1]},
    "fen":       {"q": [3, 5, 6, 4, 2], "sD": [3, 5, 4, 2, 0], "gD": [3, 4, 4, 3, 1]},
    "sosyal":    {"q": [2, 3, 3, 1, 1], "sD": [2, 3, 2, 0, 0], "gD": [2, 2, 2, 1, 0]},
    "din":       {"q": [2, 3, 3, 1, 1], "sD": [2, 2, 2, 0, 0], "gD": [2, 2, 2, 1, 0]},
    "ydil":      {"q": [2, 3, 3, 1, 1], "sD": [2, 3, 2, 1, 0], "gD": [2, 2, 2, 1, 0]},
}


def main() -> None:
    output_dir = ROOT / "sample-data"
    output_dir.mkdir(exist_ok=True)
    output_path = output_dir / "demo_asya_nur_tuncer.docx"

    student_data = build_student_data(
        name=STUDENT_NAME,
        grade=STUDENT_GRADE,
        exams=EXAMS,
        priority_topics=PRIORITY_TOPICS,
        difficulty=DIFFICULTY,
    )

    with tempfile.TemporaryDirectory() as charts_tmp:
        charts_dir = Path(charts_tmp)
        chart_paths = generate_all_charts(student_data, charts_dir)
        generate_report(student_data, output_path, charts_dir)

    print(f"✓  Rapor oluşturuldu  : {output_path}")
    print(f"   Öğrenci            : {STUDENT_NAME}")
    print(f"   Sınıf              : {STUDENT_GRADE}")
    print(f"   Sınav sayısı       : {len(EXAMS)}")
    print(f"   Ort. puan          : {student_data['avg_puan']:.1f}")
    print(f"   Risk               : {student_data['risk']['label']}")
    print(f"   Trend              : {student_data['trend']['direction']} "
          f"(delta={student_data['trend']['delta']:+.0f})")
    print()
    print("   Ders ortalamaları:")
    for sa in student_data["subject_avgs"]:
        bar = "█" * int(sa["pct"] / 5)
        print(f"   {sa['label']:18s}  {sa['avg']:5.2f} net  %{sa['pct']:5.1f}  {bar}")
    print()
    print("   Öncelikli kazanımlar:")
    for t in sorted(student_data["priority_topics"], key=lambda x: -x["priority"])[:5]:
        print(f"   [{t['priority']:3.0f}%]  {t['subject']:15s}  {t['topic']}")


if __name__ == "__main__":
    main()
