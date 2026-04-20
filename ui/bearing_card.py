"""Bearing card: HybridTrader-style direction label + SVG sparkline + bullets."""
from __future__ import annotations

import pandas as pd
import streamlit as st
import streamlit.components.v1 as components

from ui.styles import GREEN, RED, YELLOW, TEXT_DIM, TEXT_MUTED


def _compute_bearing(df: pd.DataFrame, window: int = 20) -> dict:
    if df is None or df.empty or "close" not in df.columns or len(df) < window:
        return {
            "label": "UNKNOWN", "color": TEXT_DIM,
            "desc": "Nicht genug Daten.",
            "bullets": [],
            "prices": [],
        }

    prices = df["close"].dropna().tail(window).tolist()
    net = prices[-1] - prices[0]
    total_move = sum(abs(prices[i] - prices[i-1]) for i in range(1, len(prices)))
    trend_score = (net / total_move) if total_move > 0 else 0.0

    rng = max(prices) - min(prices)
    daily_moves = [abs(prices[i] - prices[i-1]) for i in range(1, len(prices))]
    atr = sum(daily_moves) / len(daily_moves) if daily_moves else 0
    choppiness = (atr / rng) if rng > 0 else 0.5
    is_up    = trend_score > 0
    is_choppy = choppiness > 0.10

    if abs(trend_score) < 0.12:
        label, color = "RANGING", YELLOW
        desc = "Markt seitwärts – kein klarer Trend"
        bullets = [
            "Preis in einer Range ohne klaren Bias",
            "Mean-Reversion-Setups bevorzugen",
            "Breakout abwarten bevor Trendfolge",
        ]
    elif is_up and not is_choppy:
        label, color = "TRENDING UP", GREEN
        desc = "Klarer Aufwärtstrend – strukturierter Anstieg"
        bullets = [
            "Trendfolge-Setups mit erhöhter Trefferquote",
            "Dips in Richtung SMA sind Einstiegszonen",
            "Stop-Loss unter letzte Struktur setzen",
        ]
    elif is_up and is_choppy:
        label, color = "CHOPPY UP", GREEN
        desc = "Aufwärtsdrift aber unruhig – Vorsicht geboten"
        bullets = [
            "Bullisher Bias, aber RSI-Crosses zeigen Unentschlossenheit",
            "Setups valide, aber Stop-Outs häufiger",
            "Engere Stops oder kleinere Positionsgrößen",
        ]
    elif not is_up and not is_choppy:
        label, color = "TRENDING DOWN", RED
        desc = "Klarer Abwärtstrend – Druck auf Verkäuferseite"
        bullets = [
            "Short-Bias oder Cash bevorzugen",
            "Rallys in Widerstandszonen sind Short-Gelegenheiten",
            "Kein Catching-Falling-Knives",
        ]
    else:
        label, color = "CHOPPY DOWN", RED
        desc = "Abwärtsdrift aber unruhig – kein klares Bild"
        bullets = [
            "Bearisher Bias, hohe Volatilität erschwert Timing",
            "Kleine Positionsgrößen bis Struktur sich klärt",
            "Auf Volumen-Bestätigung warten",
        ]

    return {"label": label, "color": color, "desc": desc, "bullets": bullets, "prices": prices}


def _sparkline_svg(prices: list[float], color: str, width: int = 280, height: int = 80) -> str:
    if len(prices) < 2:
        return ""
    lo, hi = min(prices), max(prices)
    span = hi - lo or 1
    pad  = 4

    pts = []
    for i, v in enumerate(prices):
        x = pad + (i / (len(prices) - 1)) * (width - 2 * pad)
        y = height - pad - ((v - lo) / span) * (height - 2 * pad)
        pts.append((x, y))

    poly  = " ".join(f"{x:.1f},{y:.1f}" for x, y in pts)
    fill  = f"M {pts[0][0]:.1f},{height} " + " ".join(f"L {x:.1f},{y:.1f}" for x, y in pts) + f" L {pts[-1][0]:.1f},{height} Z"

    cid = color.lstrip("#")
    return f"""<svg width="{width}" height="{height}" viewBox="0 0 {width} {height}">
      <defs>
        <linearGradient id="bg{cid}" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0%" stop-color="{color}" stop-opacity="0.3"/>
          <stop offset="100%" stop-color="{color}" stop-opacity="0.02"/>
        </linearGradient>
      </defs>
      <path d="{fill}" fill="url(#bg{cid})"/>
      <polyline points="{poly}" fill="none" stroke="{color}" stroke-width="2"
                stroke-linejoin="round" stroke-linecap="round"/>
    </svg>"""


def render(df: pd.DataFrame, coin_id: str) -> None:
    b       = _compute_bearing(df)
    label   = b["label"]
    color   = b["color"]
    desc    = b["desc"]
    bullets = b["bullets"]
    prices  = b["prices"]

    tint_map = {GREEN: "0,208,132", RED: "255,68,85", YELLOW: "245,197,66", TEXT_DIM: "150,150,150"}
    rgb = tint_map.get(color, "150,150,150")

    spark = _sparkline_svg(prices, color)

    bullets_html = "".join(
        f'<li style="margin:4px 0;font-size:13px;color:rgba(220,220,220,0.75)">{b}</li>'
        for b in bullets
    )

    html = f"""<!DOCTYPE html><html><head><meta charset="utf-8">
<style>
  * {{ box-sizing:border-box; margin:0; padding:0; }}
  body {{ background:transparent; font-family:-apple-system,BlinkMacSystemFont,'Inter',sans-serif; }}
  .card {{
    background: rgba({rgb}, 0.07);
    border: 1px solid rgba({rgb}, 0.2);
    border-radius: 12px;
    padding: 1.1rem 1.2rem;
  }}
  .title {{
    font-size: 13px; text-transform: uppercase; letter-spacing: 0.12em;
    color: #ffffff; font-weight: 800; margin-bottom: 0.7rem;
  }}
  .label {{
    font-size: 2.2rem; font-weight: 800; letter-spacing: 0.06em;
    color: {color}; text-align: center; line-height: 1.1; margin-bottom: 0.6rem;
  }}
  .chart {{ margin: 0.3rem 0 0.5rem; }}
  .desc {{ font-size: 12.5px; color: rgba(220,220,220,0.7); margin-bottom: 0.5rem; font-style: italic; }}
  ul {{ padding-left: 1.1rem; list-style: disc; }}
</style>
</head><body>
<div class="card">
  <div class="title">Bearing</div>
  <div class="label">{label}</div>
  <div class="chart">{spark}</div>
  <div class="desc">{desc}</div>
  <ul>{bullets_html}</ul>
</div>
</body></html>"""

    components.html(html, height=320, scrolling=False)
