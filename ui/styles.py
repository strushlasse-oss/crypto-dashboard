"""Global CSS injection. Call inject() once near the top of app.py."""
from __future__ import annotations

import streamlit as st

BG      = "#080808"
PANEL   = "rgba(255,255,255,0.03)"
PANEL_2 = "rgba(255,255,255,0.05)"
BORDER  = "rgba(255,255,255,0.07)"
BORDER_HOVER = "rgba(0,208,132,0.35)"
TEXT    = "#f0f0f0"
TEXT_DIM   = "rgba(240,240,240,0.5)"
TEXT_MUTED = "rgba(240,240,240,0.32)"

GREEN  = "#00d084"
RED    = "#ff4455"
YELLOW = "#f5c542"
BLUE   = "#4da6ff"

ACCENT      = "#00d084"
ACCENT_SOFT = "rgba(0,208,132,0.12)"
ACCENT_LINE = "rgba(0,208,132,0.45)"

CSS = f"""
<style>
  html, body, .stApp, [class*="css"] {{
    font-family: -apple-system, BlinkMacSystemFont, 'Inter', 'Segoe UI', sans-serif;
  }}
  .stApp {{ background: {BG}; color: {TEXT}; }}
  .block-container {{
    padding-top: 1.4rem; padding-bottom: 4rem; max-width: 1380px;
  }}
  section[data-testid="stSidebar"] {{
    background: #0c0c0c;
    border-right: 1px solid {BORDER};
  }}
  h1, h2, h3, h4 {{ letter-spacing: -0.02em; font-weight: 700; }}
  h1 {{ font-size: 1.9rem; }}
  hr {{ border-color: {BORDER}; margin: 1rem 0; }}

  /* ── Hero greeting ── */
  .hero {{
    padding: 1.6rem 0 1.2rem 0;
    margin-bottom: 1.2rem;
  }}
  .hero-greeting {{
    font-size: 2.2rem; font-weight: 700;
    color: {ACCENT};
    letter-spacing: -0.03em; line-height: 1.1;
    margin: 0;
  }}
  .hero-sub {{
    display: flex; align-items: center; gap: 0.5rem;
    color: {TEXT_DIM}; font-size: 0.88rem;
    margin-top: 0.35rem;
  }}
  .hero-sub-icon {{ color: {ACCENT}; font-size: 0.9rem; }}

  /* ── Market Sessions ── */
  .sessions-grid {{
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 0.6rem;
    margin-bottom: 1.4rem;
  }}
  .session-card {{
    background: {PANEL};
    border: 1px solid {BORDER};
    border-radius: 12px;
    padding: 0.75rem 1rem;
  }}
  .session-name {{
    font-size: 0.72rem; font-weight: 700;
    letter-spacing: 0.12em; text-transform: uppercase;
    color: {TEXT_DIM}; margin-bottom: 0.25rem;
  }}
  .session-status {{
    font-size: 0.78rem; font-weight: 600;
    display: flex; align-items: center; gap: 0.4rem;
  }}
  .session-dot {{
    width: 7px; height: 7px; border-radius: 50%; flex-shrink: 0;
  }}
  .session-dot-open  {{ background: {ACCENT}; box-shadow: 0 0 8px {ACCENT}; }}
  .session-dot-closed {{ background: rgba(255,255,255,0.18); }}
  .session-time {{
    font-size: 0.76rem; color: {TEXT_MUTED}; margin-top: 0.15rem;
  }}

  /* ── Capital Flow ── */
  .flow-header {{
    display: flex; align-items: center; justify-content: space-between;
    margin-bottom: 0.8rem;
  }}
  .flow-row {{
    display: grid;
    grid-template-columns: 90px 1fr 60px;
    gap: 10px; align-items: center;
    margin: 5px 0;
  }}
  .flow-label {{
    font-size: 0.78rem; font-weight: 600; color: {TEXT_DIM};
    font-family: 'SF Mono', 'JetBrains Mono', monospace;
  }}
  .flow-bar-bg {{
    background: rgba(255,255,255,0.05);
    height: 6px; border-radius: 3px; overflow: hidden;
    position: relative;
  }}
  .flow-bar-fill {{
    height: 100%; border-radius: 3px;
    transition: width 0.4s ease;
  }}
  .flow-value {{
    font-size: 0.78rem; font-weight: 700;
    text-align: right;
    font-feature-settings: "tnum";
  }}

  /* ── pcard primitive ── */
  .pcard {{
    background: {PANEL};
    border: 1px solid {BORDER};
    border-radius: 14px;
    padding: 1.1rem 1.25rem;
    transition: border-color .2s ease;
  }}
  .pcard:hover {{ border-color: {BORDER_HOVER}; }}
  .pcard-title {{
    font-size: 0.82rem; text-transform: uppercase; letter-spacing: 0.12em;
    color: #ffffff; margin: 0 0 0.55rem 0; font-weight: 800;
    display: flex; align-items: center; gap: 0.4rem;
  }}
  .pcard-big {{ font-size: 2rem; font-weight: 700; line-height: 1.05; }}
  .pcard-sub {{ font-size: 0.84rem; color: {TEXT_DIM}; margin-top: 0.2rem; }}

  /* ── Bias boxes (3-column header in detail view) ── */
  .bias-grid {{
    display: grid; grid-template-columns: repeat(3, 1fr); gap: 0.8rem;
    margin-bottom: 1.2rem;
  }}
  .bias-box {{
    background: {PANEL};
    border: 1px solid {BORDER};
    border-radius: 12px;
    padding: 0.9rem 1.1rem;
  }}
  .bias-box-label {{
    font-size: 0.7rem; text-transform: uppercase; letter-spacing: 0.12em;
    color: {TEXT_MUTED}; font-weight: 600; margin-bottom: 0.35rem;
  }}
  .bias-box-value {{
    font-size: 1.35rem; font-weight: 700; line-height: 1.1;
  }}
  .bias-conf-bar {{
    margin-top: 0.5rem;
    background: rgba(255,255,255,0.07);
    height: 4px; border-radius: 2px; overflow: hidden;
  }}
  .bias-conf-fill {{
    height: 100%; border-radius: 2px;
  }}

  /* ── AI Overview card ── */
  .ai-card {{
    background: rgba(0,208,132,0.05);
    border: 1px solid rgba(0,208,132,0.18);
    border-radius: 12px;
    padding: 1rem 1.2rem;
    margin-bottom: 1rem;
  }}
  .ai-card-header {{
    display: flex; align-items: center; gap: 0.5rem;
    font-size: 0.82rem; font-weight: 700; color: {ACCENT};
    margin-bottom: 0.6rem; letter-spacing: 0.02em;
  }}
  .ai-card-body {{
    font-size: 0.93rem; line-height: 1.6; color: {TEXT};
  }}

  /* legacy ai-block kept for fallback */
  .ai-block {{
    border-left: 2px solid {ACCENT};
    padding-left: 0.85rem; color: {TEXT};
    line-height: 1.55; font-size: 0.93rem;
  }}
  .ai-block.dim {{ border-left-color: {TEXT_DIM}; }}

  /* ── Coin header ── */
  .coin-head {{ display:flex; align-items:center; gap: 0.9rem; }}
  .coin-head img {{
    width:48px; height:48px; border-radius:50%;
    box-shadow: 0 0 0 1px rgba(255,255,255,0.08);
  }}
  .coin-name {{ font-size: 1.55rem; font-weight: 700; line-height: 1; letter-spacing:-0.02em; }}
  .coin-ticker {{ font-size: 0.82rem; color: {TEXT_DIM}; margin-top: 0.25rem; }}
  .coin-tag {{
    display:inline-block; margin-left: 0.5rem; padding: 2px 8px;
    background: {ACCENT_SOFT}; border: 1px solid {ACCENT_LINE};
    border-radius: 999px; font-size: 0.68rem; color: #a0ffe0; font-weight: 600;
  }}

  /* ── Pills ── */
  .pill {{
    display: inline-flex; align-items: center; gap: 5px;
    padding: 3px 10px; border-radius: 999px;
    font-size: 0.76rem; font-weight: 600; letter-spacing: 0.03em;
  }}
  .pill-green  {{ background: rgba(0,208,132,0.12); color: {GREEN}; border: 1px solid rgba(0,208,132,0.28); }}
  .pill-red    {{ background: rgba(255,68,85,0.12);  color: {RED};   border: 1px solid rgba(255,68,85,0.28); }}
  .pill-yellow {{ background: rgba(245,197,66,0.12); color: {YELLOW};border: 1px solid rgba(245,197,66,0.28); }}
  .pill-dim    {{ background: rgba(255,255,255,0.05); color: {TEXT_DIM}; border: 1px solid {BORDER}; }}
  .pill-blue   {{ background: rgba(77,166,255,0.12); color: {BLUE}; border: 1px solid rgba(77,166,255,0.28); }}

  /* ── Live badge ── */
  .live-badge {{
    display: inline-flex; align-items: center; gap: 5px;
    font-size: 0.72rem; font-weight: 600; color: {ACCENT};
    letter-spacing: 0.05em;
  }}
  .live-dot {{
    width: 7px; height: 7px; border-radius: 50%;
    background: {ACCENT}; box-shadow: 0 0 8px {ACCENT};
    animation: live-pulse 2s ease-in-out infinite;
  }}
  @keyframes live-pulse {{
    0%,100% {{ opacity:1; transform:scale(1); }}
    50%      {{ opacity:.5; transform:scale(.85); }}
  }}

  /* ── Price ── */
  .price-main {{
    font-size: 2.6rem; font-weight: 700; line-height: 1.05;
    letter-spacing: -0.03em; font-feature-settings: "tnum";
  }}
  .price-change-up   {{ color: {GREEN}; font-weight: 600; }}
  .price-change-down {{ color: {RED};   font-weight: 600; }}

  /* ── Tick animations ── */
  @keyframes tick-up {{
    0%   {{ opacity:0; transform:translateY(10px); }}
    100% {{ opacity:1; transform:translateY(0); }}
  }}
  @keyframes tick-down {{
    0%   {{ opacity:0; transform:translateY(-10px); }}
    100% {{ opacity:1; transform:translateY(0); }}
  }}
  .price-tick-up   {{ display:inline-block; animation: tick-up   .32s cubic-bezier(.22,1,.36,1) both; }}
  .price-tick-down {{ display:inline-block; animation: tick-down  .32s cubic-bezier(.22,1,.36,1) both; }}

  /* ── Buttons ── */
  .stButton > button {{
    border-radius: 10px; border: 1px solid {BORDER};
    background: {PANEL}; color: {TEXT};
    font-weight: 600; transition: all .18s ease;
  }}
  .stButton > button:hover {{
    border-color: {ACCENT_LINE}; background: {ACCENT_SOFT}; color: #c0ffe8;
  }}

  /* ── Segmented control ── */
  div[data-testid="stSegmentedControl"] button {{ font-weight: 600; }}
  div[data-testid="stSegmentedControl"] button[aria-selected="true"] {{
    background: {ACCENT_SOFT} !important;
    color: {ACCENT} !important;
    border-color: {ACCENT_LINE} !important;
  }}

  /* ── Expander ── */
  div[data-testid="stExpander"] {{
    border: 1px solid {BORDER} !important;
    border-radius: 12px !important;
    background: {PANEL};
  }}

  /* ── Streamlit container with border ── */
  div[data-testid="stVerticalBlockBorderWrapper"] {{
    background: {PANEL} !important;
    border: 1px solid {BORDER} !important;
    border-radius: 14px !important;
    transition: border-color .2s ease;
  }}
  div[data-testid="stVerticalBlockBorderWrapper"]:hover {{
    border-color: {BORDER_HOVER} !important;
  }}
  div[data-testid="stVerticalBlockBorderWrapper"] > div[data-testid="stVerticalBlock"] {{
    padding: 1.05rem 1.2rem;
  }}

  /* ── Metrics ── */
  div[data-testid="stMetric"] {{ background: transparent; padding:0; border:none; }}
  div[data-testid="stMetricValue"] {{ font-size:1.05rem; font-weight:600; }}

  /* ── Hover tooltip ── */
  .info-tip {{
    display:inline-flex; align-items:center; justify-content:center;
    width:16px; height:16px; margin-left:6px; border-radius:50%;
    background:rgba(255,255,255,0.06); color:{TEXT_DIM};
    font-size:0.72rem; font-weight:700; cursor:help;
    position:relative; user-select:none; border:1px solid {BORDER};
  }}
  .info-tip:hover {{ background:{ACCENT_SOFT}; color:{ACCENT}; border-color:{ACCENT_LINE}; }}
  .info-tip .info-bubble {{
    visibility:hidden; opacity:0; position:absolute; z-index:50;
    bottom:130%; left:50%; transform:translateX(-50%);
    width:260px; padding:.6rem .75rem;
    background:#0a0a0a; border:1px solid {BORDER_HOVER};
    border-radius:8px; color:{TEXT}; font-size:0.78rem;
    font-weight:400; line-height:1.4; text-align:left;
    box-shadow:0 8px 24px rgba(0,0,0,.5);
    transition:opacity .15s ease; pointer-events:none;
  }}
  .info-tip:hover .info-bubble {{ visibility:visible; opacity:1; }}

  /* ── Scrollbar ── */
  ::-webkit-scrollbar {{ width:8px; height:8px; }}
  ::-webkit-scrollbar-track {{ background:transparent; }}
  ::-webkit-scrollbar-thumb {{ background:rgba(255,255,255,0.08); border-radius:8px; }}
  ::-webkit-scrollbar-thumb:hover {{ background:{ACCENT_LINE}; }}
</style>
"""


def inject() -> None:
    st.markdown(CSS, unsafe_allow_html=True)
