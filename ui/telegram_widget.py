"""WatcherGuru Telegram feed widget."""
from __future__ import annotations

import streamlit as st
import streamlit.components.v1 as components

from data import telegram_feed


@st.fragment(run_every=45)
def render() -> None:
    st.markdown(
        "<div style='display:flex;align-items:center;justify-content:space-between;"
        "margin-bottom:0.7rem'>"
        "<div class='pcard-title' style='margin:0'>WatcherGuru · Telegram</div>"
        "<span class='live-badge'><span class='live-dot'></span>Live · 1 min</span>"
        "</div>",
        unsafe_allow_html=True,
    )

    items = telegram_feed.get_messages(limit=20)

    if not items:
        st.markdown("<div class='pcard-sub'>Feed nicht erreichbar.</div>",
                    unsafe_allow_html=True)
        return

    rows_html = ""
    for item in items:
        text = item["text"].replace('"', "&quot;").replace("<", "&lt;").replace(">", "&gt;")
        age  = item["age"]
        link = item["link"]
        is_breaking = text.upper().startswith("JUST IN") or text.upper().startswith("BREAKING")
        badge = (
            "<span style='background:rgba(255,68,68,0.18);color:#ff4444;"
            "border:1px solid rgba(255,68,68,0.35);border-radius:4px;"
            "font-size:10px;font-weight:700;padding:1px 6px;margin-right:6px;"
            "letter-spacing:0.05em'>BREAKING</span>"
            if is_breaking else ""
        )
        rows_html += f"""
        <a href="{link}" target="_blank" class="msg-item">
          <div class="msg-body">
            <div class="msg-text">{badge}{text}</div>
            {"<div class='msg-age'>" + age + " ago</div>" if age else ""}
          </div>
        </a>"""

    html = f"""<!DOCTYPE html><html><head><meta charset="utf-8">
<style>
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{ background: transparent; font-family: -apple-system, BlinkMacSystemFont, 'Inter', sans-serif; }}
  .feed {{ display:flex; flex-direction:column; max-height:500px; overflow-y:auto; padding-right:4px; }}
  .feed::-webkit-scrollbar {{ width:4px; }}
  .feed::-webkit-scrollbar-thumb {{ background:rgba(255,255,255,0.12); border-radius:4px; }}
  .msg-item {{
    display:flex; gap:10px; padding:10px 6px;
    border-bottom:1px solid rgba(255,255,255,0.07);
    text-decoration:none; color:inherit;
    border-radius:6px; transition:background .15s;
  }}
  .msg-item:hover {{ background:rgba(255,255,255,0.04); }}
  .msg-body {{ flex:1; }}
  .msg-text {{ font-size:13px; font-weight:500; line-height:1.5; color:#f0f0f0; white-space:pre-wrap; }}
  .msg-age {{ font-size:11px; color:rgba(240,240,240,0.35); margin-top:4px; }}
</style></head><body>
<div class="feed">{rows_html}</div>
</body></html>"""

    components.html(html, height=520, scrolling=False)
