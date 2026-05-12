"""Ham sınav listesinden generator'ın beklediği student_data dict'ini üretir."""
from app.features.difficulty_gap import compute_difficulty_gap
from app.features.risk import classify_risk
from app.features.trend import compute_trend

# Analiz kalitesi eşikleri
_TIER_STRONG = 5    # eğilim analizi güvenilir
_TIER_BASIC = 3     # temel karşılaştırma yapılabilir
_TIER_LIMITED = 1   # sınırlı snapshot analizi


def get_analysis_tier(exam_count: int) -> dict:
    """
    Sınav sayısına göre analiz kalitesi seviyesi döner.

    Returns:
        {"level": "strong"|"basic"|"limited", "label": str, "warning": str|None}
    """
    if exam_count >= _TIER_STRONG:
        return {"level": "strong", "label": "Güçlü Analiz", "warning": None}
    if exam_count >= _TIER_BASIC:
        return {
            "level": "basic",
            "label": "Temel Analiz",
            "warning": (
                f"{exam_count} sınav verisiyle temel karşılaştırma yapılabilir. "
                f"Eğilim yorumları ve gelişim takibi için en az {_TIER_STRONG} deneme önerilir."
            ),
        }
    return {
        "level": "limited",
        "label": "Sınırlı Analiz",
        "warning": (
            f"{exam_count} sınav verisiyle yalnızca anlık görüntü analizi yapılabilir. "
            f"Daha güvenilir içgörüler için en az {_TIER_STRONG} deneme yükleyin."
        ),
    }

SUBJECT_KEYS = ["turkce", "matematik", "fen", "sosyal", "din", "ydil"]
SUBJECT_LABELS = {
    "turkce": "Türkçe",
    "matematik": "Matematik",
    "fen": "Fen Bilimleri",
    "sosyal": "İnkılap",
    "din": "Din Kültürü",
    "ydil": "Yabancı Dil",
}
# LGS standart soru sayıları
SUBJECT_MAX_Q = {
    "turkce": 20,
    "matematik": 20,
    "fen": 20,
    "sosyal": 10,
    "din": 10,
    "ydil": 10,
}


def compute_subject_avgs(exams: list[dict]) -> list[dict]:
    """
    Sınav listesinden ders bazlı ortalama istatistikleri hesaplar.

    Her exam dict'inde: turkce, matematik, fen, sosyal, din, ydil (net) bulunmalı.
    Returns list of: {key, label, avg, max, min, pct}
    """
    result = []
    for key in SUBJECT_KEYS:
        vals = [e[key] for e in exams if key in e]
        if not vals:
            continue
        avg = sum(vals) / len(vals)
        max_q = SUBJECT_MAX_Q[key]
        result.append({
            "key": key,
            "label": SUBJECT_LABELS[key],
            "avg": round(avg, 2),
            "max": round(max(vals), 2),
            "min": round(min(vals), 2),
            "pct": round(avg / max_q * 100, 1),
        })
    return result


def build_student_data(
    name: str,
    grade: str,
    exams: list[dict],
    priority_topics: list[dict] | None = None,
    difficulty: dict | None = None,
) -> dict:
    """
    ReportGenerator.generate() için eksiksiz student_data dict'i üretir.

    Args:
        name: Öğrenci adı soyadı
        grade: Sınıf/şube — "8-A"
        exams: Her biri {date, name, publisher, turkce, matematik, fen,
                         sosyal, din, ydil, puan} içeren sınav listesi
        priority_topics: compute_priority_topics() çıktısı — opsiyonel
        difficulty: {subject_key: {"q": [...5], "sD": [...5], "gD": [...5]}} — opsiyonel

    Returns:
        student_data dict — generator ve charts modülleri doğrudan tüketir
    """
    if not exams:
        return {
            "name": name,
            "grade": grade,
            "avg_puan": 0.0,
            "risk": {"level": "sinirli", "label": "Sınırlı Analiz"},
            "trend": {"slope": 0.0, "delta": 0.0, "direction": "flat"},
            "exams": [],
            "subject_avgs": [],
            "priority_topics": priority_topics or [],
            "difficulty": difficulty or {},
            "worst_gap": None,
            "analysis_tier": get_analysis_tier(0),
        }

    scores = [e["puan"] for e in exams]
    avg_puan = sum(scores) / len(scores)
    trend = compute_trend(scores)
    risk = classify_risk(avg_puan, scores, len(exams))
    subject_avgs = compute_subject_avgs(exams)

    difficulty = difficulty or {}
    worst_gap = None
    if difficulty:
        gap_result = compute_difficulty_gap(difficulty)
        worst_gap = gap_result.get("worst_gap")

    analysis_tier = get_analysis_tier(len(exams))

    return {
        "name": name,
        "grade": grade,
        "avg_puan": round(avg_puan, 1),
        "risk": risk,
        "trend": trend,
        "exams": exams,
        "subject_avgs": subject_avgs,
        "priority_topics": priority_topics or [],
        "difficulty": difficulty,
        "worst_gap": worst_gap,
        "analysis_tier": analysis_tier,  # {"level", "label", "warning"}
    }
