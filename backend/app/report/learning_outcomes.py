"""
Tahmini konu/kazanım önerileri — yerel sözlük tabanlı MVP.

Parser'dan gerçek kazanım verisi gelmediğinde, ders bazlı düşük performans
alanlarını tahmini konu önerileriyle eşleştirir.

Tüm çıktılar estimated=True ve source="subject_performance" ile işaretlenir.
Belirli soruların hangi konudan geldiği bilinmez; yalnızca ders zayıflığından tahmin edilir.
"""

_SUBJECT_TOPICS: dict[str, list[str]] = {
    "turkce": [
        "Paragraf Yapısı (ana düşünce, konu, başlık)",
        "Sözcükte Anlam (eş anlam, karşıt anlam, mecaz)",
        "Cümlede Anlam (neden-sonuç, amaç, koşul)",
        "Söz Sanatları (teşbih, metafor, kişileştirme)",
        "Dil Bilgisi (fiil çekimi, zaman ekleri)",
        "Yazım Kuralları ve Noktalama",
    ],
    "matematik": [
        "Üslü İfadeler ve Köklü Sayılar",
        "Çarpanlar ve Katlar (EBOB, EKOK)",
        "Birinci Dereceden Denklemler",
        "Olasılık ve Veri Analizi",
        "Geometri (alan, çevre, üçgenler)",
        "Dönüşüm Geometrisi (öteleme, yansıma)",
    ],
    "fen": [
        "Basınç (katı, sıvı, gaz basıncı)",
        "Kuvvet ve Hareket (Newton Yasaları)",
        "Kalıtım, DNA ve Genetik Kod",
        "Madde ve Özellikleri (asit-baz, karışımlar)",
        "Elektrik ve Manyetizma",
        "Mevsimler ve Dünya'nın Hareketleri",
    ],
    "sosyal": [
        "Milli Mücadele ve Kurtuluş Savaşı",
        "Atatürk İlkeleri ve İnkılapları",
        "Türkiye'nin Coğrafi Bölgeleri",
        "Ekonomik Faaliyetler ve Üretim",
        "Demokrasi, İnsan Hakları ve Vatandaşlık",
    ],
    "din": [
        "İman Esasları (Allah'a, meleklere, kitaplara iman)",
        "İslam'ın Şartları ve Temel İbadetler",
        "Hz. Muhammed'in Hayatı ve Örnekliği",
        "Kur'an-ı Kerim'in Temel Bilgileri",
        "Ahlak, Değerler ve Sosyal Hayat",
    ],
    "ydil": [
        "Daily Life & Teen Activities",
        "Friendship & Relationships",
        "Tourism & Directions",
        "Science & Technology",
        "Environment & Nature",
    ],
}

_SUBJECT_MAX_Q: dict[str, int] = {
    "turkce": 20,
    "matematik": 20,
    "fen": 20,
    "sosyal": 10,
    "din": 10,
    "ydil": 10,
}

_SUBJECT_LABELS: dict[str, str] = {
    "turkce": "Türkçe",
    "matematik": "Matematik",
    "fen": "Fen Bilimleri",
    "sosyal": "İnkılap",
    "din": "Din Kültürü",
    "ydil": "Yabancı Dil",
}


def generate_estimated_topics(
    exams: list[dict],
    subject_avgs: list[dict] | None = None,
    max_topics: int = 6,
) -> list[dict]:
    """
    Sınav verilerinden ders bazlı tahmini konu önerileri üretir.

    Öncelik sırası: subject_avgs varsa kullan (zaten hesaplanmış),
    yoksa ham exams listesinden ders bazlı ortalama hesapla.

    Returns:
        Her öğe {rank, subject, topic, q, d, y, b, success, priority,
                 estimated=True, source="subject_performance"} içerir.
        Veri yoksa boş liste döner.
    """
    if subject_avgs:
        sorted_subjects = sorted(subject_avgs, key=lambda s: s.get("pct", 100.0))
    elif exams:
        nets: dict[str, list[float]] = {}
        for exam in exams:
            for key in _SUBJECT_LABELS:
                val = exam.get(key)
                if val is not None:
                    nets.setdefault(key, []).append(float(val))

        if not nets:
            return []

        sorted_subjects = sorted(
            [
                {
                    "key": key,
                    "label": _SUBJECT_LABELS[key],
                    "avg": sum(v) / len(v),
                    "pct": (sum(v) / len(v)) / _SUBJECT_MAX_Q.get(key, 20) * 100,
                }
                for key, v in nets.items()
            ],
            key=lambda s: s.get("pct", 100.0),
        )
    else:
        return []

    results: list[dict] = []
    rank = 1
    for subj in sorted_subjects:
        key = subj.get("key", "")
        topics = _SUBJECT_TOPICS.get(key, [])
        if not topics:
            continue

        pct = subj.get("pct", 50.0)
        priority = max(10.0, min(95.0, round(100.0 - pct, 1)))

        results.append({
            "rank": rank,
            "subject": subj.get("label", key),
            "topic": topics[0],
            "q": 0,
            "d": 0,
            "y": 0,
            "b": 0,
            "success": round(pct, 1),
            "priority": priority,
            "estimated": True,
            "source": "subject_performance",
        })
        rank += 1
        if rank > max_topics:
            break

    return results
