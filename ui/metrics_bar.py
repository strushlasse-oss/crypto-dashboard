"""Metrics bar: Fear & Greed, BTC Dominance, Total Market Cap — with sparklines."""
from __future__ import annotations

import math

import streamlit as st
import streamlit.components.v1 as components

from data import fear_greed as fg
from data import global_metrics as gm
from ui.styles import GREEN, RED, TEXT_DIM, TEXT_MUTED


def _fmt_cap(v: float | None) -> str:
    if v is None:
        return "–"
    if v >= 1e12:
        return f"${v / 1e12:.2f}T"
    if v >= 1e9:
        return f"${v / 1e9:.1f}B"
    return f"${v:,.0f}"


def _fmt_pct(v: float | None) -> str:
    if v is None:
        return "–"
    arrow = "▲" if v >= 0 else "▼"
    return f"{arrow} {v:+.2f}%"


def _fng_label(v: int) -> str:
    if v < 25:
        return "Extreme Fear"
    if v < 45:
        return "Fear"
    if v < 55:
        return "Neutral"
    if v < 75:
        return "Greed"
    return "Extreme Greed"


def _sparkline(values: list[float], color: str, width: int = 120, height: int = 40) -> str:
    """Generate an inline SVG sparkline path."""
    if len(values) < 2:
        return f"<svg width='{width}' height='{height}'></svg>"
    lo, hi = min(values), max(values)
    span = hi - lo or 1
    pad = 3
    pts = []
    for i, v in enumerate(values):
        x = pad + (i / (len(values) - 1)) * (width - 2 * pad)
        y = height - pad - ((v - lo) / span) * (height - 2 * pad)
        pts.append((x, y))

    # Polyline points
    poly = " ".join(f"{x:.1f},{y:.1f}" for x, y in pts)

    # Fill area path
    fill_pts = f"M {pts[0][0]:.1f},{height} " + " ".join(f"L {x:.1f},{y:.1f}" for x, y in pts) + f" L {pts[-1][0]:.1f},{height} Z"

    return f"""<svg width="{width}" height="{height}" viewBox="0 0 {width} {height}">
      <defs>
        <linearGradient id="sg_{color[1:]}" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0%" stop-color="{color}" stop-opacity="0.25"/>
          <stop offset="100%" stop-color="{color}" stop-opacity="0"/>
        </linearGradient>
      </defs>
      <path d="{fill_pts}" fill="url(#sg_{color[1:]})" />
      <polyline points="{poly}" fill="none" stroke="{color}" stroke-width="1.5" stroke-linejoin="round" stroke-linecap="round"/>
    </svg>"""


def _gauge_svg(fng_val: int, fng_color: str) -> str:
    arc_len  = 132
    dashoff  = arc_len - (fng_val / 100) * arc_len
    return f"""<svg viewBox="0 0 100 60" width="100" height="60">
      <defs>
        <linearGradient id="fg" x1="0%" y1="0%" x2="100%" y2="0%">
          <stop offset="0%"   stop-color="#E63946"/>
          <stop offset="50%"  stop-color="#E9C46A"/>
          <stop offset="100%" stop-color="#2A9D8F"/>
        </linearGradient>
      </defs>
      <path d="M 8 54 A 42 42 0 1 1 92 54"
            fill="none" stroke="rgba(255,255,255,0.1)" stroke-width="8" stroke-linecap="round"/>
      <path d="M 8 54 A 42 42 0 1 1 92 54"
            fill="none" stroke="url(#fg)" stroke-width="8" stroke-linecap="round"
            stroke-dasharray="{arc_len}" stroke-dashoffset="{dashoff:.1f}"/>
      <text x="50" y="50" text-anchor="middle"
            font-size="15" font-weight="700" fill="{fng_color}"
            font-family="-apple-system,BlinkMacSystemFont,Inter,sans-serif">{fng_val}</text>
    </svg>"""


@st.fragment(run_every=120)
def render(fng_value: int | None = None) -> None:
    glob    = gm.get_global()
    history = gm.get_market_cap_history(days=30)
    fng_hist = fg.get_fear_greed_history(days=30)

    fng_val = fng_value
    if fng_val is None:
        try:
            fng_list = fg.get_fear_greed(limit=1)
            fng_val  = int(fng_list[0]["value"]) if fng_list else None
        except Exception:
            fng_val = None

    fng_color = fg.classify_color(fng_val) if fng_val is not None else "#888"
    fng_label = _fng_label(fng_val) if fng_val is not None else "–"

    btc_d  = glob.get("btc_dominance")
    mc     = glob.get("market_cap_usd")
    mc_chg = glob.get("market_cap_change")
    mc_color = GREEN if (mc_chg or 0) >= 0 else RED

    # Sparklines
    fng_spark = _sparkline(fng_hist, fng_color) if fng_hist else ""
    btcd_vals = history.get("btc_d", [])
    mc_vals   = history.get("mc", [])
    btcd_color = "#f7a832"
    btcd_trend = btcd_vals[-1] - btcd_vals[0] if len(btcd_vals) >= 2 else 0
    btcd_spark = _sparkline(btcd_vals, btcd_color) if btcd_vals else ""
    mc_spark   = _sparkline(mc_vals, mc_color if mc_vals else GREEN) if mc_vals else ""

    gauge = _gauge_svg(fng_val, fng_color) if fng_val is not None else f"<div style='width:100px;height:60px'></div>"

    btcd_str  = f"{btcd:.1f}%" if (btcd := btc_d) else "–"
    mc_chg_str = _fmt_pct(mc_chg)

    html = f"""<!DOCTYPE html><html><head><meta charset="utf-8">
<style>
  * {{ box-sizing:border-box; margin:0; padding:0; }}
  body {{ background:transparent; font-family:-apple-system,BlinkMacSystemFont,'Inter',sans-serif; }}
  .bar {{
    display:flex; align-items:stretch; gap:0;
    background:rgba(255,255,255,0.03);
    border:1px solid rgba(255,255,255,0.07);
    border-radius:12px; overflow:hidden;
  }}
  .cell {{
    flex:1; padding:1rem 1.2rem;
    border-right:1px solid rgba(255,255,255,0.06);
    display:flex; flex-direction:column; gap:6px;
  }}
  .cell:last-child {{ border-right:none; }}
  .label {{
    font-size:13px; text-transform:uppercase; letter-spacing:0.1em;
    color:#ffffff; font-weight:800;
  }}
  .val-lg {{ font-size:1.8rem; font-weight:700; line-height:1; }}
  .sub {{ font-size:12px; font-weight:600; }}
  .dim {{ color:rgba(240,240,240,0.32); font-weight:400; }}
  .row {{ display:flex; align-items:center; justify-content:space-between; gap:8px; }}
  /* Tooltip */
  .info {{ position:relative; display:inline-block; }}
  .info-btn {{
    width:15px; height:15px; border-radius:50%;
    background:rgba(255,255,255,0.1); border:none; cursor:pointer;
    color:rgba(255,255,255,0.4); font-size:9px; font-weight:700;
    display:inline-flex; align-items:center; justify-content:center;
    vertical-align:middle; margin-left:5px;
  }}
  .tooltip {{
    display:none; position:absolute; bottom:calc(100% + 6px); left:50%;
    transform:translateX(-50%);
    background:#1e1e1e; border:1px solid rgba(255,255,255,0.12);
    border-radius:7px; padding:8px 10px; width:200px;
    font-size:11px; line-height:1.5; color:#ccc; z-index:99;
    pointer-events:none;
  }}
  .info:hover .tooltip {{ display:block; }}
</style>
</head><body>
<div class="bar">

  <!-- Fear & Greed -->
  <div class="cell">
    <div class="row">
      <div class="label">
        Fear &amp; Greed
        <span class="info"><button class="info-btn">i</button>
          <div class="tooltip">Misst Angst vs. Gier im Markt (0 = Extreme Fear, 100 = Extreme Greed). Basiert auf Volatilität, Volumen, Social Media &amp; Dominanz.</div>
        </span>
      </div>
    </div>
    <div class="row" style="align-items:flex-end">
      {gauge}
      <div style="flex:1">
        <div style="font-size:1.2rem;font-weight:700;color:{fng_color};line-height:1">{fng_label}</div>
        <div style="margin-top:6px">{fng_spark}</div>
        <div style="font-size:10px;color:rgba(240,240,240,0.3);margin-top:2px">30 Tage</div>
      </div>
    </div>
  </div>

  <!-- BTC Dominance -->
  <div class="cell">
    <div class="label">
      BTC Dominance
      <span class="info"><button class="info-btn">i</button>
        <div class="tooltip">Anteil von Bitcoin an der gesamten Krypto-Marktkapitalisierung. Steigt oft bei Risk-off-Stimmung oder Altcoin-Schwäche.</div>
      </span>
    </div>
    <div class="val-lg" style="color:{btcd_color}">{btcd_str}</div>
    {btcd_spark}
    <div style="font-size:10px;color:rgba(240,240,240,0.3)">30 Tage</div>
  </div>

  <!-- Total Market Cap -->
  <div class="cell">
    <div class="label">
      Total Market Cap
      <span class="info"><button class="info-btn">i</button>
        <div class="tooltip">Summe aller Krypto-Marktkapitalisierungen in USD. Wichtiger Makro-Indikator für den Gesamtmarkt.</div>
      </span>
    </div>
    <div class="val-lg" style="color:#e0e0e0">{_fmt_cap(mc)}</div>
    <div class="sub" style="color:{mc_color}">{mc_chg_str} <span class="dim">· 24h</span></div>
    {mc_spark}
    <div style="font-size:10px;color:rgba(240,240,240,0.3)">30 Tage</div>
  </div>

</div>
</body></html>"""

    components.html(html, height=200, scrolling=False)
