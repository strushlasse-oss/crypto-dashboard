"""Edge Factor – deterministic 0-100 score from price + indicator data.

No API calls; pure function over the indicator-enriched DataFrame plus
optional Fear & Greed value. Used to drive the headline score donut and
to feed the AI-overview prompt.
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd


@dataclass
class EdgeComponent:
    name: str
    points: float
    max_points: float
    note: str


@dataclass
class EdgeResult:
    score: int
    label: str
    color: str
    headline: str
    comment: str
    components: list[EdgeComponent]


_LABELS = {
    "low": ("Low Edge – stay patient", "#ff4466"),
    "mixed": ("Mixed Signals", "#ffcc00"),
    "strong": ("Strong Setup", "#00ff88"),
}


def _score_rsi(rsi: float | None) -> EdgeComponent:
    if rsi is None or np.isnan(rsi):
        return EdgeComponent("RSI", 0, 20, "RSI nicht verfügbar")
    if 45 <= rsi <= 60:
        return EdgeComponent("RSI", 20, 20, f"RSI {rsi:.0f} im Sweet-Spot")
    if 35 <= rsi < 45 or 60 < rsi <= 70:
        return EdgeComponent("RSI", 12, 20, f"RSI {rsi:.0f} brauchbar")
    if 25 <= rsi < 35 or 70 < rsi <= 80:
        return EdgeComponent("RSI", 5, 20, f"RSI {rsi:.0f} grenzwertig")
    return EdgeComponent("RSI", 0, 20, f"RSI {rsi:.0f} extrem")


def _score_macd(df: pd.DataFrame) -> EdgeComponent:
    if "macd" not in df or "macd_signal" not in df or "macd_hist" not in df:
        return EdgeComponent("MACD", 0, 20, "MACD fehlt")
    tail = df.tail(3).dropna(subset=["macd", "macd_signal", "macd_hist"])
    if tail.empty:
        return EdgeComponent("MACD", 0, 20, "MACD fehlt")
    last = tail.iloc[-1]
    macd, sig, hist = float(last["macd"]), float(last["macd_signal"]), float(last["macd_hist"])
    hist_growing = len(tail) >= 2 and hist > float(tail.iloc[-2]["macd_hist"])

    if macd > sig and hist > 0 and hist_growing:
        return EdgeComponent("MACD", 20, 20, "MACD bullish & wachsend")
    if macd > sig and hist > 0:
        return EdgeComponent("MACD", 12, 20, "MACD über Signal")
    if hist < 0 and hist_growing:
        return EdgeComponent("MACD", 8, 20, "MACD-Hist erholt sich")
    return EdgeComponent("MACD", 0, 20, "MACD bearish")


def _score_vs_sma(close: float | None, sma: float | None, label: str,
                  bullish_threshold: float, neutral_band: float) -> EdgeComponent:
    if close is None or sma is None or np.isnan(close) or np.isnan(sma):
        return EdgeComponent(label, 0, 20, f"{label} fehlt")
    diff_pct = (close - sma) / sma * 100
    if diff_pct > bullish_threshold:
        return EdgeComponent(label, 20, 20, f"Preis {diff_pct:+.1f}% über {label}")
    if diff_pct > 0:
        return EdgeComponent(label, 14, 20, f"Preis knapp über {label}")
    if diff_pct > -neutral_band:
        return EdgeComponent(label, 8, 20, f"Preis nahe {label}")
    return EdgeComponent(label, 0, 20, f"Preis {diff_pct:+.1f}% unter {label}")


def _score_volume(df: pd.DataFrame) -> EdgeComponent:
    if "volume" not in df:
        return EdgeComponent("Volumen", 0, 20, "Volumen fehlt")
    vol = df["volume"].dropna()
    if len(vol) < 30:
        return EdgeComponent("Volumen", 0, 20, "Zu wenige Daten")
    avg7 = vol.tail(7).mean()
    avg30 = vol.tail(30).mean()
    if avg30 == 0:
        return EdgeComponent("Volumen", 0, 20, "Volumen 0")
    ratio = avg7 / avg30
    if ratio > 1.1:
        return EdgeComponent("Volumen", 20, 20, f"Volumen ×{ratio:.2f} (steigend)")
    if ratio >= 1.0:
        return EdgeComponent("Volumen", 12, 20, f"Volumen ×{ratio:.2f} (stabil)")
    return EdgeComponent("Volumen", 5, 20, f"Volumen ×{ratio:.2f} (rückläufig)")


def _score_fng(fng_value: int | None, tech_bullish: bool) -> EdgeComponent:
    if fng_value is None:
        return EdgeComponent("F&G", 12, 20, "F&G unbekannt – neutral gewertet")
    if fng_value < 25:
        if tech_bullish:
            return EdgeComponent("F&G", 20, 20, f"Extreme Fear ({fng_value}) + bullishe Technik = Kontra-Setup")
        return EdgeComponent("F&G", 14, 20, f"Extreme Fear ({fng_value}) – Boden-Zone")
    if fng_value > 75:
        return EdgeComponent("F&G", 5, 20, f"Greed ({fng_value}) – Top-Risiko")
    if 45 <= fng_value <= 55:
        return EdgeComponent("F&G", 12, 20, f"Neutral ({fng_value})")
    return EdgeComponent("F&G", 10, 20, f"F&G {fng_value}")


def compute(df: pd.DataFrame, fng_value: int | None = None) -> EdgeResult:
    """Compute the Edge Factor from an indicator-enriched DataFrame.

    df must contain the columns produced by analysis.indicators.compute_indicators
    (close, rsi_14, sma_50, sma_200, macd*, volume optional).
    """
    if df is None or df.empty:
        return EdgeResult(0, *_LABELS["low"], "Keine Daten",
                          "Es liegen keine ausreichenden Daten vor.", [])

    last = df.iloc[-1]
    close = float(last["close"]) if "close" in df else None
    rsi = float(last["rsi_14"]) if "rsi_14" in df and not pd.isna(last["rsi_14"]) else None
    sma50 = float(last["sma_50"]) if "sma_50" in df and not pd.isna(last["sma_50"]) else None
    sma200 = float(last["sma_200"]) if "sma_200" in df and not pd.isna(last["sma_200"]) else None

    tech_bullish = bool(close and sma50 and close > sma50)

    components = [
        _score_rsi(rsi),
        _score_macd(df),
        _score_vs_sma(close, sma50, "SMA50", bullish_threshold=3, neutral_band=3),
        _score_vs_sma(close, sma200, "SMA200 (Regime)", bullish_threshold=2, neutral_band=2),
        _score_volume(df),
        _score_fng(fng_value, tech_bullish),
    ]

    raw = sum(c.points for c in components)
    score = int(round(min(100, raw / 1.2)))

    if score >= 67:
        headline, color = _LABELS["strong"]
        bucket = "strong"
    elif score >= 34:
        headline, color = _LABELS["mixed"]
        bucket = "mixed"
    else:
        headline, color = _LABELS["low"]
        bucket = "low"

    comment = _build_comment(components, bucket)
    return EdgeResult(score, bucket, color, headline, comment, components)


def _build_comment(components: list[EdgeComponent], bucket: str) -> str:
    sorted_c = sorted(components, key=lambda c: c.points / c.max_points, reverse=True)
    top = sorted_c[:2]
    bottom = sorted_c[-2:]

    pos = ", ".join(c.note for c in top if c.points >= c.max_points * 0.6)
    neg = ", ".join(c.note for c in bottom if c.points <= c.max_points * 0.4)

    if bucket == "strong":
        lead = "Mehrere Signale stützen einen konstruktiven Setup."
    elif bucket == "mixed":
        lead = "Bild ist gemischt – Bestätigung abwarten."
    else:
        lead = "Wenig Edge gerade – Geduld zahlt sich aus."

    parts = [lead]
    if pos:
        parts.append(f"Pro: {pos}.")
    if neg:
        parts.append(f"Contra: {neg}.")
    return " ".join(parts)
