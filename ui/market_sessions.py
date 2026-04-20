"""Market sessions: horizontal 24h timeline calendar view."""
from __future__ import annotations

from datetime import datetime, timezone

import streamlit as st
import streamlit.components.v1 as components

SESSIONS = [
    {"name": "Sydney",   "open": 22, "close": 7,  "color": "#4db8ff"},
    {"name": "Tokyo",    "open": 0,  "close": 9,  "color": "#ff9f43"},
    {"name": "London",   "open": 8,  "close": 17, "color": "#a29bfe"},
    {"name": "New York", "open": 13, "close": 22, "color": "#00d084"},
]


def _is_open(open_h: int, close_h: int, h: float) -> bool:
    if open_h < close_h:
        return open_h <= h < close_h
    return h >= open_h or h < close_h


@st.fragment(run_every=60)
def render() -> None:
    now_utc  = datetime.now(timezone.utc)
    now_h    = now_utc.hour + now_utc.minute / 60
    time_str = now_utc.strftime("%H:%M UTC")

    # Layout constants
    label_w = 80   # px for session name column
    bar_w   = 600  # px for the 24h bar
    row_h   = 28
    row_gap = 8
    axis_h  = 24
    pad_top = 8
    total_h = pad_top + axis_h + len(SESSIONS) * (row_h + row_gap) + 10

    # Current time line x position
    now_x = label_w + (now_h / 24) * bar_w

    # Tick marks every 4 hours
    ticks_html = ""
    for hh in range(0, 25, 4):
        x = label_w + (hh / 24) * bar_w
        label = f"{hh:02d}:00" if hh < 24 else "00:00"
        ticks_html += (
            f'<line x1="{x}" y1="{pad_top + axis_h - 5}" x2="{x}" y2="{pad_top + axis_h}" '
            f'stroke="rgba(255,255,255,0.15)" stroke-width="1"/>'
            f'<text x="{x}" y="{pad_top + axis_h - 8}" text-anchor="middle" '
            f'font-size="9" fill="rgba(255,255,255,0.3)" font-family="Inter,sans-serif">{label}</text>'
        )

    # Session bars
    bars_html = ""
    for i, s in enumerate(SESSIONS):
        y      = pad_top + axis_h + i * (row_h + row_gap)
        cy     = y + row_h / 2
        open_h = s["open"]
        close_h = s["close"]
        color  = s["color"]
        is_open = _is_open(open_h, close_h, now_h)
        opacity = "1" if is_open else "0.35"

        # Session name
        bars_html += (
            f'<text x="{label_w - 8}" y="{cy + 4}" text-anchor="end" '
            f'font-size="11" font-weight="600" fill="rgba(255,255,255,{0.85 if is_open else 0.4})" '
            f'font-family="Inter,sans-serif">{s["name"]}</text>'
        )

        # Background track
        bars_html += (
            f'<rect x="{label_w}" y="{y}" width="{bar_w}" height="{row_h}" rx="5" '
            f'fill="rgba(255,255,255,0.04)"/>'
        )

        # Session block(s)
        if open_h < close_h:
            x1 = label_w + (open_h / 24) * bar_w
            w1 = ((close_h - open_h) / 24) * bar_w
            bars_html += (
                f'<rect x="{x1:.1f}" y="{y}" width="{w1:.1f}" height="{row_h}" rx="5" '
                f'fill="{color}" opacity="{opacity}"/>'
            )
        else:
            # Wraps midnight — two segments
            w1 = ((24 - open_h) / 24) * bar_w
            w2 = (close_h / 24) * bar_w
            bars_html += (
                f'<rect x="{label_w:.1f}" y="{y}" width="{w1:.1f}" height="{row_h}" rx="5" '
                f'fill="{color}" opacity="{opacity}"/>'
                f'<rect x="{label_w + bar_w - w1:.1f}" y="{y}" width="{w1:.1f}" height="{row_h}" rx="5" '
                f'fill="{color}" opacity="{opacity}"/>'
                f'<rect x="{label_w:.1f}" y="{y}" width="{w2:.1f}" height="{row_h}" rx="5" '
                f'fill="{color}" opacity="{opacity}"/>'
            )

        # Open indicator dot on left if open
        if is_open:
            bars_html += (
                f'<circle cx="{label_w + 10}" cy="{cy}" r="4" fill="{color}" '
                f'opacity="0.9"/>'
            )

    # Current time line + label
    now_line = (
        f'<line x1="{now_x:.1f}" y1="{pad_top}" x2="{now_x:.1f}" y2="{total_h - 4}" '
        f'stroke="rgba(255,255,255,0.7)" stroke-width="1.5" stroke-dasharray="4,3"/>'
        f'<rect x="{now_x - 22:.1f}" y="{pad_top}" width="44" height="16" rx="4" '
        f'fill="rgba(255,255,255,0.12)"/>'
        f'<text x="{now_x:.1f}" y="{pad_top + 11}" text-anchor="middle" '
        f'font-size="9" font-weight="700" fill="white" font-family="Inter,sans-serif">{time_str.replace(" UTC","")}</text>'
    )

    svg = f"""<svg width="{label_w + bar_w}" height="{total_h}"
     viewBox="0 0 {label_w + bar_w} {total_h}"
     xmlns="http://www.w3.org/2000/svg">
  {ticks_html}
  {bars_html}
  {now_line}
</svg>"""

    html = f"""<!DOCTYPE html><html><head><meta charset="utf-8">
<style>
  * {{ box-sizing:border-box; margin:0; padding:0; }}
  body {{ background:transparent; overflow:hidden; }}
  .header {{
    display:flex; justify-content:space-between; align-items:center;
    margin-bottom:6px;
    font-family:-apple-system,BlinkMacSystemFont,'Inter',sans-serif;
  }}
  .label {{ font-size:13px; text-transform:uppercase; letter-spacing:0.12em;
             color:#ffffff; font-weight:800; }}
  .utc {{ font-size:13px; color:rgba(255,255,255,0.6); font-weight:600; }}
</style>
</head><body>
<div class="header">
  <span class="label">Markt-Sessions</span>
  <span class="utc">{time_str}</span>
</div>
{svg}
</body></html>"""

    components.html(html, height=total_h + 30, scrolling=False)
