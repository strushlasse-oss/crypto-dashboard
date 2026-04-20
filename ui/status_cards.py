"""Three status cards: Market Mood, Technical Structure, Momentum.

All logic is rule-based; no API calls. Each function returns a dict
{label, pill_class, explanation} so the renderer stays dumb.
"""
from __future__ import annotations

import pandas as pd
import streamlit as st

from ui import edge_score
from ui.styles import GREEN, RED, YELLOW


def _pill(label: str, klass: str) -> str:
    return f"<span class='pill {klass}'>{label}</span>"


def market_mood(fng_value: int | None) -> dict:
    if fng_value is None:
        return {"label": "Unknown", "klass": "pill-dim", "color": "#888",
                "explanation": "Fear & Greed Index nicht erreichbar."}
    if fng_value < 25:
        return {"label": "RISK-OFF", "klass": "pill-red", "color": RED,
                "explanation": f"Extreme Fear ({fng_value}). Marktteilnehmer "
                               "kapitulieren – historisch oft Boden-Zone."}
    if fng_value < 45:
        return {"label": "RISK-OFF", "klass": "pill-red", "color": RED,
                "explanation": f"Vorsicht überwiegt ({fng_value}). Liquidität "
                               "zurückhaltend."}
    if fng_value <= 55:
        return {"label": "NEUTRAL", "klass": "pill-yellow", "color": YELLOW,
                "explanation": f"Markt unentschlossen ({fng_value}). "
                               "Catalysts treiben die Richtung."}
    if fng_value <= 75:
        return {"label": "RISK-ON", "klass": "pill-green", "color": GREEN,
                "explanation": f"Optimismus dominiert ({fng_value}). "
                               "Trends laufen, FOMO baut sich auf."}
    return {"label": "RISK-ON", "klass": "pill-green", "color": GREEN,
            "explanation": f"Greed ({fng_value}). Top-Risiko steigt – "
                           "Trailing-Stops sinnvoll."}


def technical_structure(df: pd.DataFrame) -> dict:
    if df is None or df.empty:
        return {"label": "Unknown", "klass": "pill-dim",
                "explanation": "Keine Daten verfügbar."}
    last = df.iloc[-1]
    close = last.get("close")
    sma50 = last.get("sma_50")
    sma200 = last.get("sma_200")
    bb_upper = last.get("bb_upper")
    bb_lower = last.get("bb_lower")

    recent = df.tail(3)
    breakout_up = ("bb_upper" in df and "close" in df
                   and (recent["close"] > recent["bb_upper"]).any())
    breakout_dn = ("bb_lower" in df and "close" in df
                   and (recent["close"] < recent["bb_lower"]).any())

    if close and sma50 and sma200 and close > sma50 > sma200:
        return {"label": "Bullish", "klass": "pill-green",
                "explanation": "Preis über SMA50 über SMA200 – klassische "
                               "Aufwärts-Struktur."}
    if close and sma50 and sma200 and close < sma50 < sma200:
        return {"label": "Bearish", "klass": "pill-red",
                "explanation": "Preis unter SMA50 unter SMA200 – Downtrend "
                               "intakt."}
    if breakout_up:
        return {"label": "Breakout", "klass": "pill-green",
                "explanation": "Close über oberem Bollinger – Ausbruch nach oben."}
    if breakout_dn:
        return {"label": "Breakdown", "klass": "pill-red",
                "explanation": "Close unter unterem Bollinger – Ausbruch nach unten."}
    return {"label": "Consolidating", "klass": "pill-yellow",
            "explanation": "Preis bewegt sich zwischen den Glättungen – Range."}


def momentum(df: pd.DataFrame) -> dict:
    if df is None or df.empty or "rsi_14" not in df:
        return {"label": "Unknown", "klass": "pill-dim",
                "explanation": "Kein RSI verfügbar."}
    last = df.iloc[-1]
    rsi = last.get("rsi_14")
    macd_hist = last.get("macd_hist")
    if rsi is None or pd.isna(rsi):
        return {"label": "Unknown", "klass": "pill-dim",
                "explanation": "Kein RSI verfügbar."}
    rsi = float(rsi)

    if rsi > 70:
        return {"label": "Overbought", "klass": "pill-red",
                "explanation": f"RSI {rsi:.0f} – überkauft, Korrekturrisiko erhöht."}
    if rsi < 30:
        return {"label": "Oversold", "klass": "pill-green",
                "explanation": f"RSI {rsi:.0f} – überverkauft, Reversion-Setup."}

    hist_growing = False
    if "macd_hist" in df and len(df) >= 2:
        prev = df["macd_hist"].iloc[-2]
        if pd.notna(prev) and pd.notna(macd_hist):
            hist_growing = float(macd_hist) > float(prev)
    if 50 <= rsi <= 65 and hist_growing:
        return {"label": "Building", "klass": "pill-green",
                "explanation": f"RSI {rsi:.0f} steigt, MACD-Hist wächst – "
                               "Momentum baut sich auf."}
    if 35 <= rsi < 50 and hist_growing:
        return {"label": "Building", "klass": "pill-yellow",
                "explanation": f"RSI {rsi:.0f} dreht, MACD-Hist erholt – "
                               "frühes Momentum."}
    return {"label": "Neutral", "klass": "pill-yellow",
            "explanation": f"RSI {rsi:.0f}, kein klares Momentum-Signal."}


def render_row(df, fng_value: int | None) -> None:
    """Render the three status cards as a row."""
    mood = market_mood(fng_value)
    struct = technical_structure(df)
    mom = momentum(df)

    c1, c2, c3 = st.columns(3)

    with c1, st.container(border=True):
        st.markdown(
            f"<div class='pcard-title'>Market Mood</div>"
            f"<div style='display:flex;justify-content:space-between;align-items:flex-start'>"
            f"<div>{_pill(mood['label'], mood['klass'])}</div>"
            f"<div style='font-size:1.6rem;font-weight:700;color:{mood['color']}'>"
            f"{fng_value if fng_value is not None else '–'}</div>"
            f"</div>",
            unsafe_allow_html=True,
        )
        if fng_value is not None:
            st.plotly_chart(
                edge_score.gauge(fng_value, mood["label"], mood["color"], height=140),
                width="stretch", config={"displayModeBar": False},
            )
        st.markdown(
            f"<div class='pcard-sub'>{mood['explanation']}</div>",
            unsafe_allow_html=True,
        )

    with c2, st.container(border=True):
        st.markdown(
            f"<div class='pcard-title'>Technical Structure</div>"
            f"<div style='margin:0.4rem 0'>{_pill(struct['label'], struct['klass'])}</div>"
            f"<div class='pcard-sub'>{struct['explanation']}</div>",
            unsafe_allow_html=True,
        )

    with c3, st.container(border=True):
        st.markdown(
            f"<div class='pcard-title'>Momentum</div>"
            f"<div style='margin:0.4rem 0'>{_pill(mom['label'], mom['klass'])}</div>"
            f"<div class='pcard-sub'>{mom['explanation']}</div>",
            unsafe_allow_html=True,
        )
