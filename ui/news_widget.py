"""Crypto breaking news feed widget."""
from __future__ import annotations

import streamlit as st
import streamlit.components.v1 as components

from data import rss_feed


def render() -> None:
    st.markdown(
        "<div style='display:flex;align-items:center;justify-content:space-between;"
        "margin-bottom:0.7rem'>"
        "<div class='pcard-title' style='margin:0'>Breaking News</div>"
        "<span class='live-badge'><span class='live-dot'></span>Live · 2 min</span>"
        "</div>",
        unsafe_allow_html=True,
    )

    items = rss_feed.get_news(limit=30)

    if not items:
        st.markdown("<div class='pcard-sub'>Keine News geladen.</div>",
                    unsafe_allow_html=True)
        return

    rows_html = ""
    for item in items:
        title = item["title"].replace("'", "&#39;").replace('"', "&quot;")
        link  = item["link"]
        age   = item["age"]
        src   = item["source"]
        color = item["color"]

        rows_html += f"""
        <a href="{link}" target="_blank" class="news-item">
          <div class="news-dot" style="background:{color};box-shadow:0 0 6px {color}"></div>
          <div class="news-body">
            <div class="news-title">{title}</div>
            <div class="news-meta">
              <span style="color:{color};font-weight:600">{src}</span>
              {"&nbsp;·&nbsp;" + age if age else ""}
            </div>
          </div>
        </a>"""

    html = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{
    background: transparent;
    font-family: -apple-system, BlinkMacSystemFont, 'Inter', sans-serif;
    overflow-x: hidden;
  }}
  .feed {{
    display: flex;
    flex-direction: column;
    max-height: 480px;
    overflow-y: auto;
    padding-right: 4px;
  }}
  .feed::-webkit-scrollbar {{ width: 4px; }}
  .feed::-webkit-scrollbar-track {{ background: transparent; }}
  .feed::-webkit-scrollbar-thumb {{ background: rgba(255,255,255,0.12); border-radius: 4px; }}
  .news-item {{
    display: flex;
    align-items: flex-start;
    gap: 10px;
    padding: 10px 0;
    border-bottom: 1px solid rgba(255,255,255,0.07);
    text-decoration: none;
    color: inherit;
    transition: background .15s;
    border-radius: 4px;
    padding-left: 4px;
  }}
  .news-item:hover {{ background: rgba(255,255,255,0.04); }}
  .news-dot {{
    width: 8px;
    height: 8px;
    border-radius: 50%;
    flex-shrink: 0;
    margin-top: 5px;
  }}
  .news-body {{ flex: 1; min-width: 0; }}
  .news-title {{
    font-size: 13px;
    font-weight: 500;
    line-height: 1.45;
    color: #f0f0f0;
    display: -webkit-box;
    -webkit-line-clamp: 2;
    -webkit-box-orient: vertical;
    overflow: hidden;
  }}
  .news-meta {{
    font-size: 11px;
    color: rgba(240,240,240,0.4);
    margin-top: 3px;
  }}
</style>
</head>
<body>
<div class="feed">
{rows_html}
</div>
</body>
</html>"""

    components.html(html, height=500, scrolling=False)
