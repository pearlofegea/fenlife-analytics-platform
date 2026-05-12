"""Matplotlib ile FENlife markalı grafikler — PNG olarak kaydedilir, DOCX'e gömülür."""
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import numpy as np

FENLIFE_BLUE = "#1B5E8C"
FENLIFE_ORANGE = "#E87722"
FENLIFE_TEAL = "#2A8A8A"
GRAY = "#A8A29E"
BG = "#FAFAF9"

SUBJECT_COLORS = {
    "turkce": "#E87722",
    "matematik": "#1B5E8C",
    "fen": "#2A8A8A",
    "sosyal": "#7C5CBF",
    "din": "#D97706",
    "ydil": "#059669",
}
SUBJECT_LABELS = {
    "turkce": "Türkçe",
    "matematik": "Mat",
    "fen": "Fen",
    "sosyal": "İnk",
    "din": "Din",
    "ydil": "YDil",
}

plt.rcParams.update({
    "font.family": "sans-serif",
    "axes.spines.top": False,
    "axes.spines.right": False,
    "axes.facecolor": BG,
    "figure.facecolor": "white",
})


def _save(fig: plt.Figure, path: Path) -> Path:
    fig.savefig(path, dpi=150, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    return path


def puan_trend_chart(exams: list[dict], output_dir: Path) -> Path:
    """Area chart: puan hareketi. Tek sınav için bar chart'a düşer."""
    dates = [e["date"][-5:] for e in exams]  # MM-DD
    scores = [e["puan"] for e in exams]

    fig, ax = plt.subplots(figsize=(7, 3))

    if len(scores) == 1:
        ax.bar(dates, scores, color=FENLIFE_BLUE, alpha=0.8, width=0.4)
        ax.set_title("Puan (Tek Sınav)", fontsize=11, fontweight="bold", color="#1c1917", pad=8)
    else:
        ax.fill_between(dates, scores, alpha=0.15, color=FENLIFE_BLUE)
        ax.plot(dates, scores, color=FENLIFE_BLUE, linewidth=2, marker="o", markersize=4)
        if len(scores) >= 2:
            x = np.arange(len(scores))
            slope, intercept = np.polyfit(x, scores, 1)
            trend_line = [slope * i + intercept for i in x]
            ax.plot(dates, trend_line, "--", color=GRAY, linewidth=1, alpha=0.7)
        ax.set_title("Puan Trendi", fontsize=11, fontweight="bold", color="#1c1917", pad=8)

    ax.set_ylabel("LGS Puanı", fontsize=8, color=GRAY)
    ax.tick_params(axis="both", labelsize=8, colors="#78716c")
    ax.yaxis.set_minor_locator(mticker.AutoMinorLocator())
    fig.tight_layout()
    return _save(fig, output_dir / "puan_trend.png")


def ders_basari_chart(subject_avgs: list[dict], output_dir: Path) -> Path:
    """Horizontal bar: ders bazlı başarı oranı."""
    labels = [s["label"] for s in subject_avgs]
    pcts = [s["pct"] for s in subject_avgs]
    colors = [SUBJECT_COLORS.get(s["key"], FENLIFE_BLUE) for s in subject_avgs]

    fig, ax = plt.subplots(figsize=(5, 3))
    bars = ax.barh(labels, pcts, color=colors, height=0.55)
    ax.bar_label(bars, fmt="%d%%", padding=4, fontsize=8, color="#44403c")
    ax.set_xlim(0, 110)
    ax.set_xlabel("Başarı Oranı (%)", fontsize=8, color=GRAY)
    ax.set_title("Ders Bazlı Başarı", fontsize=11, fontweight="bold", color="#1c1917", pad=8)
    ax.tick_params(axis="both", labelsize=9, colors="#44403c")
    ax.invert_yaxis()
    fig.tight_layout()
    return _save(fig, output_dir / "ders_basari.png")


def zorluk_matrix_chart(difficulty: dict, output_dir: Path) -> Path:
    """Grouped bar: öğrenci vs kurum zorluk karşılaştırması (tüm dersler ortalama)."""
    levels = ["Çok Kolay", "Kolay", "Orta", "Zor", "Çok Zor"]
    student_avgs = []
    general_avgs = []

    for i in range(5):
        s_vals, g_vals = [], []
        for d in difficulty.values():
            total_q = d["q"][i] if i < len(d["q"]) else 0
            if total_q > 0:
                s_vals.append((d["sD"][i] / total_q) * 100)
                g_vals.append((d["gD"][i] / total_q) * 100)
        student_avgs.append(np.mean(s_vals) if s_vals else 0)
        general_avgs.append(np.mean(g_vals) if g_vals else 0)

    x = np.arange(len(levels))
    width = 0.35

    fig, ax = plt.subplots(figsize=(6, 3))
    ax.bar(x - width / 2, student_avgs, width, label="Öğrenci", color=FENLIFE_BLUE, alpha=0.85)
    ax.bar(x + width / 2, general_avgs, width, label="Kurum", color=GRAY, alpha=0.85)
    ax.set_xticks(x)
    ax.set_xticklabels(levels, fontsize=8, color="#44403c")
    ax.set_ylabel("Başarı %", fontsize=8, color=GRAY)
    ax.set_title("Zorluk Karşılaştırması", fontsize=11, fontweight="bold", color="#1c1917", pad=8)
    ax.legend(fontsize=8)
    ax.tick_params(axis="y", labelsize=8, colors="#78716c")
    fig.tight_layout()
    return _save(fig, output_dir / "zorluk_matrix.png")


def kazanimlar_chart(priority_topics: list[dict], output_dir: Path) -> Path:
    """Horizontal bar: top 5 öncelikli kazanımlar."""
    top5 = priority_topics[:5]
    labels = [f"{t['subject'][:3]} · {t['topic'][:30]}{'…' if len(t['topic']) > 30 else ''}" for t in top5]
    pcts = [t["priority"] for t in top5]

    fig, ax = plt.subplots(figsize=(6, 3))
    bars = ax.barh(labels[::-1], pcts[::-1], color=FENLIFE_ORANGE, height=0.5, alpha=0.85)
    ax.bar_label(bars, fmt="%d%%", padding=4, fontsize=8, color="#44403c")
    ax.set_xlim(0, 115)
    ax.set_xlabel("Öncelik Puanı (%)", fontsize=8, color=GRAY)
    ax.set_title("Öncelikli Kazanımlar", fontsize=11, fontweight="bold", color="#1c1917", pad=8)
    ax.tick_params(axis="both", labelsize=8, colors="#44403c")
    fig.tight_layout()
    return _save(fig, output_dir / "kazanimlar.png")


def generate_all_charts(student_data: dict, output_dir: Path) -> dict[str, Path]:
    """
    Tüm grafikleri üret. Veri eksikse ilgili grafik atlanır.

    Returns:
        {"puan_trend": Path, "ders_basari": Path, "zorluk_matrix": Path, "kazanimlar": Path}
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    charts: dict[str, Path] = {}

    exams = student_data.get("exams") or []
    subject_avgs = student_data.get("subject_avgs") or []
    difficulty = student_data.get("difficulty") or {}
    priority_topics = student_data.get("priority_topics") or []

    if exams:
        charts["puan_trend"] = puan_trend_chart(exams, output_dir)
    if subject_avgs:
        charts["ders_basari"] = ders_basari_chart(subject_avgs, output_dir)
    if difficulty:
        charts["zorluk_matrix"] = zorluk_matrix_chart(difficulty, output_dir)
    if priority_topics:
        charts["kazanimlar"] = kazanimlar_chart(priority_topics, output_dir)

    return charts
