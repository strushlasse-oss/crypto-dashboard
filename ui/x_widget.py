"""Official Twitter/X embedded timeline widget via st.components."""
from __future__ import annotations

import streamlit as st
import streamlit.components.v1 as components

from ui.styles import ACCENT, TEXT_DIM, TEXT_MUTED, BORDER


def render(username: str = "WatcherGuru", height: int = 600) -> None:
    st.markdown(
        f"<div style='display:flex;align-items:center;justify-content:space-between;"
        f"margin-bottom:0.6rem'>"
        f"<div class='pcard-title' style='margin:0'>X · @{username}</div>"
        f"<span class='live-badge'><span class='live-dot'></span>Live</span>"
        f"</div>",
        unsafe_allow_html=True,
    )

    embed_html = f"""
    <style>
      body {{ margin: 0; background: #080808; }}
      .twitter-timeline {{ border-radius: 12px !important; }}
    </style>
    <a class="twitter-timeline"
       data-theme="dark"
       data-chrome="noheader nofooter noborders transparent"
       data-tweet-limit="10"
       data-dnt="true"
       href="https://twitter.com/{username}">
      Tweets by @{username}
    </a>
    <script async src="https://platform.twitter.com/widgets.js" charset="utf-8"></script>
    """

    components.html(embed_html, height=height, scrolling=True)
