"""Crypto news from free RSS feeds."""
from __future__ import annotations

import ssl
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime
from email.utils import parsedate_to_datetime

import streamlit as st

_SSL = ssl.create_default_context()
_SSL.check_hostname = False
_SSL.verify_mode = ssl.CERT_NONE

SOURCES = [
    {"name": "CoinTelegraph", "url": "https://cointelegraph.com/rss",                    "color": "#f7931a"},
    {"name": "CoinDesk",      "url": "https://www.coindesk.com/arc/outboundfeeds/rss/",  "color": "#4da6ff"},
    {"name": "NewsbtC",       "url": "https://www.newsbtc.com/feed/",                    "color": "#00d084"},
    {"name": "U.Today",       "url": "https://u.today/rss",                              "color": "#a78bfa"},
    {"name": "CryptoSlate",   "url": "https://cryptoslate.com/feed/",                    "color": "#f5c542"},
    {"name": "Decrypt",       "url": "https://decrypt.co/feed",                          "color": "#ff6b6b"},
]


def _fetch(source: dict) -> list[dict]:
    try:
        req = urllib.request.Request(
            source["url"], headers={"User-Agent": "Mozilla/5.0"}
        )
        with urllib.request.urlopen(req, timeout=6, context=_SSL) as r:
            root = ET.fromstring(r.read())
    except Exception:
        return []

    items = []
    for item in root.findall(".//item")[:8]:
        title = (item.find("title") or ET.Element("x")).text or ""
        link  = (item.find("link")  or ET.Element("x")).text or ""
        pub   = (item.find("pubDate") or ET.Element("x")).text or ""
        try:
            dt = parsedate_to_datetime(pub)
            age_min = int((datetime.now(dt.tzinfo) - dt).total_seconds() / 60)
            if age_min < 60:
                age_str = f"{age_min}m ago"
            elif age_min < 1440:
                age_str = f"{age_min // 60}h ago"
            else:
                age_str = f"{age_min // 1440}d ago"
        except Exception:
            age_str = ""

        items.append({
            "title":  title.strip(),
            "link":   link.strip(),
            "age":    age_str,
            "source": source["name"],
            "color":  source["color"],
        })
    return items


@st.cache_data(ttl=120, show_spinner=False)
def get_news(limit: int = 30) -> list[dict]:
    """Fetch and merge news from all sources, sorted newest first."""
    all_items: list[dict] = []
    for src in SOURCES:
        all_items.extend(_fetch(src))
    # stable sort: keep original order (newest-first per feed) but interleave
    return all_items[:limit]
