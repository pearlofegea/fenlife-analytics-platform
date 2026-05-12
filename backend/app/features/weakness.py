"""Zayıf kazanım tespiti — öncelik sıralaması."""
from app.parser.schemas import KazanimBreakdown


SUBJECTS_TR = {
    "turkce": "Türkçe",
    "matematik": "Matematik",
    "fen": "Fen Bilimleri",
    "sosyal": "İnkılap",
    "din": "Din Kültürü",
    "ydil": "Yabancı Dil",
}


def compute_priority_topics(
    kazanimlar: list[KazanimBreakdown],
    top_n: int = 10,
) -> list[dict]:
    """
    Kazanımları öncelik puanına göre sırala.

    Öncelik = (1 - başarı_oranı) × soru_sayısı × tekrar_faktörü
    Returns top_n kazanım dicts: subject, topic, q, d, y, b, success, priority
    """
    scored = []
    for k in kazanimlar:
        if k.total_questions == 0:
            continue
        success_pct = k.success_pct
        # priority_pct: sağlanmışsa kullan, yoksa hesapla
        if k.priority_pct is not None:
            priority_pct = k.priority_pct
        else:
            # Net loss potential: wrong+blank rate weighted by question count
            error_rate = 1.0 - (success_pct / 100.0)
            priority_pct = round(error_rate * 100, 1)

        scored.append({
            "subject": k.subject,
            "topic": k.kazanim_name,
            "q": k.total_questions,
            "d": k.correct,
            "y": k.wrong,
            "b": k.blank,
            "success": round(success_pct, 1),
            "priority": round(priority_pct, 1),
        })

    scored.sort(key=lambda x: x["priority"], reverse=True)
    return scored[:top_n]
