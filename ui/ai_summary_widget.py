"""AI 12h market summary widget."""
from __future__ import annotations

import streamlit as st
import streamlit.components.v1 as components

from data import ai_summary as ais
from ui.styles import ACCENT, TEXT_DIM, TEXT_MUTED


@st.fragment(run_every=900)
def render() -> None:
    key_present = bool(ais._api_key())

    header_html = (
        "<div style='display:flex;align-items:center;justify-content:space-between;margin-bottom:0.6rem'>"
        "<div class='pcard-title' style='margin:0'>AI Marktanalyse · 12h</div>"
        "<span class='live-badge'><span class='live-dot'></span>15 min</span>"
        "</div>"
    )
    st.markdown(header_html, unsafe_allow_html=True)

    if not key_present:
        st.markdown(
            f"<div style='color:{TEXT_DIM};font-size:13px;padding:0.5rem 0'>"
            f"Kein API-Key gesetzt. Füge <code>ANTHROPIC_API_KEY</code> in "
            f"<code>.streamlit/secrets.toml</code> ein.</div>",
            unsafe_allow_html=True,
        )
        return

    with st.spinner("Analysiere Markt…"):
        text = ais.get_summary()

    if not text:
        st.markdown(
            f"<div style='color:{TEXT_DIM};font-size:13px'>Analyse nicht verfügbar.</div>",
            unsafe_allow_html=True,
        )
        return

    # Parse verdict line and bullets
    lines  = [l.strip() for l in text.splitlines() if l.strip()]
    verdict_line = ""
    verdict_tag  = ""
    verdict_rest = ""
    bullets = []

    for line in lines:
        if line.upper().startswith("VERDICT:"):
            verdict_line = line[8:].strip()
            if "–" in verdict_line:
                verdict_tag, verdict_rest = verdict_line.split("–", 1)
            elif "-" in verdict_line:
                verdict_tag, verdict_rest = verdict_line.split("-", 1)
            else:
                verdict_tag, verdict_rest = verdict_line, ""
            verdict_tag  = verdict_tag.strip()
            verdict_rest = verdict_rest.strip()
        elif line.startswith("•"):
            bullets.append(line[1:].strip())

    # Color by verdict
    tag_upper = verdict_tag.upper()
    if "BULLISH" in tag_upper and "NEUTRAL" not in tag_upper and "BEARISH" not in tag_upper:
        v_color = "#00d084"
        bg, border = "rgba(0,208,132,0.06)", "rgba(0,208,132,0.2)"
    elif "BEARISH" in tag_upper and "NEUTRAL" not in tag_upper:
        v_color = "#ff4455"
        bg, border = "rgba(255,68,85,0.06)", "rgba(255,68,85,0.2)"
    else:
        v_color = "#f5c542"
        bg, border = "rgba(245,197,66,0.06)", "rgba(245,197,66,0.18)"

    def esc(s: str) -> str:
        return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

    bullets_html = "".join(
        f'<div style="display:flex;gap:8px;align-items:flex-start;margin-top:5px">'
        f'<span style="color:{v_color};font-weight:700;margin-top:1px">›</span>'
        f'<span style="font-size:13px;font-weight:500;color:rgba(225,225,225,0.9);line-height:1.45">{esc(b)}</span>'
        f'</div>'
        for b in bullets
    )

    html = f"""<!DOCTYPE html><html><head><meta charset="utf-8">
<style>
  * {{ box-sizing:border-box; margin:0; padding:0; }}
  body {{ background:transparent; font-family:-apple-system,BlinkMacSystemFont,'Inter',sans-serif; }}
  .card {{
    background:{bg}; border:1px solid {border};
    border-radius:9px; padding:0.7rem 0.9rem 0.9rem;
  }}
  .top {{ display:flex; align-items:center; gap:10px; margin-bottom:8px; flex-wrap:wrap; }}
  .badge {{
    background:rgba(0,208,132,0.15); color:#00d084;
    border:1px solid rgba(0,208,132,0.3); border-radius:4px;
    font-size:9px; font-weight:700; letter-spacing:0.08em;
    padding:2px 6px; text-transform:uppercase; white-space:nowrap;
  }}
  .verdict-tag {{ font-size:14px; font-weight:900; color:{v_color}; white-space:nowrap; }}
  .verdict-rest {{ font-size:12.5px; font-weight:500; color:rgba(210,210,210,0.85); }}
  .sep {{ width:1px; height:14px; background:rgba(255,255,255,0.12); }}
</style>
</head><body>
<div class="card">
  <div class="top">
    <div class="badge">⚡ AI</div>
    <div class="sep"></div>
    <span class="verdict-tag">{esc(verdict_tag)}</span>
    {'<span class="verdict-rest"> – ' + esc(verdict_rest) + '</span>' if verdict_rest else ''}
  </div>
  {bullets_html}
</div>
</body></html>"""

    n_bullets = len(bullets)
    components.html(html, height=90 + n_bullets * 34, scrolling=False)
