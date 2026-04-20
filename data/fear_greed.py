"""Fear & Greed Index from alternative.me. Free, no key."""
from __future__ import annotations

import requests
import streamlit as st

URL = "https://api.alternative.me/fng/"


@st.cache_data(ttl=600, show_spinner=False)
def get_fear_greed(limit: int = 1) -> list[dict]:
    """Returns list with {value, value_classification, timestamp, ...}, newest first."""
    try:
        resp = requests.get(URL, params={"limit": limit, "format": "json"}, timeout=10)
        resp.raise_for_status()
        payload = resp.json()
        return payload.get("data", [])
    except Exception:
        return []


@st.cache_data(ttl=3600, show_spinner=False)
def get_fear_greed_history(days: int = 30) -> list[int]:
    """Returns list of F&G values oldest→newest."""
    try:
        resp = requests.get(URL, params={"limit": days, "format": "json"}, timeout=10)
        resp.raise_for_status()
        data = resp.json().get("data", [])
        return [int(d["value"]) for d in reversed(data)]
    except Exception:
        return []


def classify_color(value: int) -> str:
    if value < 25:
        return "#E63946"
    if value < 45:
        return "#F4A261"
    if value < 55:
        return "#E9C46A"
    if value < 75:
        return "#A8DADC"
    return "#2A9D8F"
