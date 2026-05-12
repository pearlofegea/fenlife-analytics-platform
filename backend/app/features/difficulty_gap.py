"""Zorluk seviyelerinde öğrenci ↔ kurum farkı hesaplama."""

DIFFICULTY_LEVELS = ["Çok Kolay", "Kolay", "Orta", "Zor", "Çok Zor"]


def compute_difficulty_gap(difficulty: dict) -> dict:
    """
    Her ders × zorluk seviyesi için başarı farkını hesapla.

    Args:
        difficulty: {subject_key: {"q": [...], "sD": [...], "gD": [...]}}
                    q=soru sayısı, sD=öğrenci doğru, gD=kurum doğru

    Returns:
        {
          "worst_gap": {"subject", "level", "gap", "student_pct", "general_pct"} | None,
          "gaps": [{subject, level, student_pct, general_pct, gap}, ...]
        }
    """
    gaps = []
    for subject_key, d in difficulty.items():
        for i, level in enumerate(DIFFICULTY_LEVELS):
            total_q = d["q"][i] if i < len(d["q"]) else 0
            if total_q == 0:
                continue
            s_pct = (d["sD"][i] / total_q) * 100
            g_pct = (d["gD"][i] / total_q) * 100
            gaps.append({
                "subject": subject_key,
                "level": level,
                "student_pct": round(s_pct, 1),
                "general_pct": round(g_pct, 1),
                "gap": round(g_pct - s_pct, 1),
            })

    worst = None
    if gaps:
        worst_entry = max(gaps, key=lambda x: x["gap"])
        if worst_entry["gap"] > 0:
            worst = worst_entry

    return {"worst_gap": worst, "gaps": gaps}
