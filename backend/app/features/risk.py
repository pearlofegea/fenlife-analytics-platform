"""Risk sınıflandırma — kural tabanlı + ML fallback."""
from app.features.trend import compute_trend


def classify_risk(
    avg_score: float,
    scores: list[float],
    exam_count: int,
    min_exams: int = 5,
) -> dict:
    """
    Risk seviyesini belirler.

    Returns:
        {"level": "dusuk"|"orta"|"yuksek"|"sinirli", "label": str}
    """
    if exam_count < min_exams:
        return {"level": "sinirli", "label": "Sınırlı Analiz"}

    trend = compute_trend(scores)
    last = scores[-1]
    score = 0

    if avg_score < 320:
        score += 2
    elif avg_score < 370:
        score += 1
    if trend["direction"] == "down":
        score += 2
    elif trend["direction"] == "flat":
        score += 1
    if last < avg_score - 30:
        score += 1

    if score >= 4:
        return {"level": "yuksek", "label": "Yüksek Öncelikli"}
    if score >= 2:
        return {"level": "orta", "label": "Orta Öncelikli"}
    return {"level": "dusuk", "label": "Stabil Gelişim"}
