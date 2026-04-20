"""Flow card: HybridTrader-style volume health indicator."""
from __future__ import annotations

import pandas as pd
import streamlit as st
import streamlit.components.v1 as components

from ui.styles import GREEN, RED, YELLOW, TEXT_DIM, TEXT_MUTED


def _compute_flow(df: pd.DataFrame) -> dict:
    if df is None or df.empty or "volume" not in df.columns:
        return {"label": "UNKNOWN", "ratio": 1.0, "color": TEXT_DIM,
                "bullets": ["Keine Volumendaten verfügbar."]}
    vol = df["volume"].dropna()
    if len(vol) < 30:
        return {"label": "UNKNOWN", "ratio": 1.0, "color": TEXT_DIM,
                "bullets": ["Zu wenige Daten."]}
    avg7  = float(vol.tail(7).mean())
    avg30 = float(vol.tail(30).mean())
    ratio = avg7 / avg30 if avg30 > 0 else 1.0

    if ratio < 0.7:
        return {
            "label": "THIN", "ratio": ratio, "color": YELLOW,
            "desc": "Geringes Volumen – wenig Marktpartizipation",
            "bullets": [
                "Preisbewegungen können irreführend sein",
                "Fills zu quoted prices nicht garantiert",
                "Positionsgrößen reduzieren",
            ],
        }
    if ratio <= 1.35:
        return {
            "label": "HEALTHY", "ratio": ratio, "color": GREEN,
            "desc": "Normale Marktpartizipation – Tape gut strukturiert",
            "bullets": [
                "Volumen im erwarteten Bereich",
                "Fills sollten zu quoted prices ausgeführt werden",
                "Flow unterstützt normale Positionsgrößen",
            ],
        }
    return {
        "label": "CROWDED", "ratio": ratio, "color": RED,
        "desc": "Erhöhtes Volumen – Markt überfüllt",
        "bullets": [
            "Erhöhtes Reversal-Risiko bei Gewinnmitnahmen",
            "Slippage bei großen Orders möglich",
            "Vorsicht bei aggressiven Entries",
        ],
    }


def _waveform_svg(color: str) -> str:
    bars = [
        (0, 10, 4, 8),
        (6, 6,  4, 12),
        (12, 2, 4, 16),
        (18, 6, 4, 12),
        (24, 10, 4, 8),
    ]
    rects = "".join(
        f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="2" fill="{color}"/>'
        for x, y, w, h in bars
    )
    return f'<svg width="32" height="22" viewBox="0 0 32 22" fill="none">{rects}</svg>'


def render(df: pd.DataFrame) -> None:
    flow   = _compute_flow(df)
    label  = flow["label"]
    ratio  = flow["ratio"]
    color  = flow["color"]
    desc   = flow.get("desc", "")
    bullets = flow["bullets"]

    # Position on bar: ratio 0.5 → 0%, 1.0 → 50%, 1.5+ → 100%
    pos_pct = min(96, max(4, (ratio - 0.5) / 1.0 * 100))

    # Tint RGB from color
    tint_map = {GREEN: "0,208,132", RED: "255,68,85", YELLOW: "245,197,66", TEXT_DIM: "150,150,150"}
    rgb = tint_map.get(color, "150,150,150")

    bullets_html = "".join(
        f'<li style="margin:4px 0;font-size:13px;color:rgba(220,220,220,0.75)">{b}</li>'
        for b in bullets
    )

    wave = _waveform_svg(color)

    html = f"""<!DOCTYPE html><html><head><meta charset="utf-8">
<style>
  * {{ box-sizing:border-box; margin:0; padding:0; }}
  body {{ background:transparent; font-family:-apple-system,BlinkMacSystemFont,'Inter',sans-serif; }}
  .card {{
    background: rgba({rgb}, 0.07);
    border: 1px solid rgba({rgb}, 0.2);
    border-radius: 12px;
    padding: 1.1rem 1.2rem;
    height: 100%;
  }}
  .title {{
    font-size: 13px; text-transform: uppercase; letter-spacing: 0.12em;
    color: #ffffff; font-weight: 800; margin-bottom: 0.7rem;
  }}
  .center {{ text-align: center; margin-bottom: 0.9rem; }}
  .label {{ font-size: 2.2rem; font-weight: 800; letter-spacing: 0.08em; color: {color}; line-height: 1.1; }}
  .desc {{ font-size: 12.5px; color: rgba(220,220,220,0.7); margin-top: 0.5rem; font-style: italic; }}
  .bar-wrap {{ position: relative; margin: 0.6rem 0 0.3rem; }}
  .bar {{
    height: 8px; border-radius: 4px;
    background: linear-gradient(90deg, #8a7a20 0%, {GREEN} 45%, {GREEN} 55%, #7a1a1a 100%);
  }}
  .dot {{
    position: absolute; top: -4px;
    left: {pos_pct:.1f}%; transform: translateX(-50%);
    width: 16px; height: 16px; border-radius: 50%;
    background: white; border: 2.5px solid {color};
    box-shadow: 0 0 10px {color};
  }}
  .bar-labels {{
    display: flex; justify-content: space-between;
    font-size: 10px; color: rgba(240,240,240,0.3);
    margin-top: 0.3rem; margin-bottom: 0.8rem;
  }}
  ul {{ padding-left: 1.1rem; list-style: disc; }}
</style>
</head><body>
<div class="card">
  <div class="title">Flow</div>
  <div class="center">
    {wave}
    <div class="label">{label}</div>
  </div>
  <div class="bar-wrap">
    <div class="bar"></div>
    <div class="dot"></div>
  </div>
  <div class="bar-labels">
    <span>Thin</span><span>Healthy</span><span>Crowded</span>
  </div>
  <div class="desc">{desc}</div>
  <ul style="margin-top:0.7rem">{bullets_html}</ul>
</div>
</body></html>"""

    components.html(html, height=320, scrolling=False)
