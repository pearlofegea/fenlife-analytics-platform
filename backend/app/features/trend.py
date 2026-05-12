"""Trend hesaplama — doğrusal regresyon eğimi, ivme, volatilite."""
import numpy as np


def compute_trend(scores: list[float]) -> dict:
    """
    Puan serisinin trendini hesaplar.

    Returns:
        {"slope": float, "delta": float, "direction": "up"|"down"|"flat"}
    """
    if len(scores) < 2:
        return {"slope": 0.0, "delta": 0.0, "direction": "flat"}

    x = np.arange(len(scores))
    y = np.array(scores)
    slope = np.polyfit(x, y, 1)[0]
    delta = float(y[-1] - y[0])
    direction = "up" if slope > 2 else "down" if slope < -2 else "flat"

    return {"slope": float(slope), "delta": delta, "direction": direction}
