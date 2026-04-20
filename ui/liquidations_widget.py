"""Liquidation pressure widget for BTC, ETH, SOL."""
from __future__ import annotations

import streamlit as st

from data import liquidations as liq
from ui.styles import GREEN, RED, TEXT_DIM, TEXT_MUTED, ACCENT

_COINS = [
    ("bitcoin",  "BTC"),
    ("ethereum", "ETH"),
    ("solana",   "SOL"),
]

_PRESSURE_COLOR = {
    "longs":   RED,
    "shorts":  GREEN,
    "neutral": "#888",
}

_PRESSURE_LABEL = {
    "longs":   "Longs gefährdet",
    "shorts":  "Shorts gefährdet",
    "neutral": "Neutral",
}


@st.fragment(run_every=60)
def render() -> None:
    st.markdown(
        "<div style='display:flex;align-items:center;justify-content:space-between;"
        "margin-bottom:0.7rem'>"
        "<div class='pcard-title' style='margin:0'>Liquidation Pressure</div>"
        "<span class='live-badge'><span class='live-dot'></span>Live · 1 min</span>"
        "</div>",
        unsafe_allow_html=True,
    )

    rows_html = ""
    for coin_id, label in _COINS:
        d = liq.get_liquidation_data(coin_id)
        if not d:
            rows_html += f"<div style='color:{TEXT_DIM};font-size:12px;padding:6px 0'>{label} — keine Daten</div>"
            continue

        long_pct  = d["long_pct"]
        short_pct = d["short_pct"]
        pressure  = d["pressure"]
        oi_chg    = d["oi_change"]
        p_color   = _PRESSURE_COLOR[pressure]
        p_label   = _PRESSURE_LABEL[pressure]
        oi_str    = f"{oi_chg:+.2f}%" if oi_chg is not None else "–"
        oi_color  = GREEN if (oi_chg or 0) >= 0 else RED

        rows_html += f"""
        <div style="margin-bottom:0.9rem">
          <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:4px">
            <span style="font-size:13px;font-weight:700;color:#e0e0e0">{label}</span>
            <span style="font-size:11px;font-weight:600;color:{p_color}">{p_label}</span>
          </div>
          <!-- L/S bar -->
          <div style="display:flex;height:10px;border-radius:5px;overflow:hidden;margin-bottom:4px">
            <div style="width:{long_pct:.1f}%;background:{GREEN};opacity:0.85"></div>
            <div style="width:{short_pct:.1f}%;background:{RED};opacity:0.85"></div>
          </div>
          <div style="display:flex;justify-content:space-between;font-size:10px;color:{TEXT_MUTED}">
            <span style="color:{GREEN}">Longs {long_pct:.1f}%</span>
            <span style="color:{TEXT_DIM};font-size:10px">OI 1h: <span style="color:{oi_color}">{oi_str}</span></span>
            <span style="color:{RED}">Shorts {short_pct:.1f}%</span>
          </div>
        </div>"""

    st.markdown(
        f"<div style='padding:0.1rem 0'>{rows_html}</div>",
        unsafe_allow_html=True,
    )
