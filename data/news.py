"""CryptoPanic news feed. Optional — only active when CRYPTOPANIC_TOKEN is set."""
from __future__ import annotations

import os

import requests
import streamlit as st

URL = "https://cryptopanic.com/api/v1/posts/"


def is_enabled() -> bool:
    return bool(os.getenv("CRYPTOPANIC_TOKEN"))


@st.cache_data(ttl=300, show_spinner=False)
def get_news(currencies: list[str] | None = None, limit: int = 15) -> list[dict]:
    token = os.getenv("CRYPTOPANIC_TOKEN")
    if not token:
        return []
    params: dict = {"auth_token": token, "public": "true"}
    if currencies:
        params["currencies"] = ",".join(currencies)
    resp = requests.get(URL, params=params, timeout=10)
    resp.raise_for_status()
    results = resp.json().get("results", [])[:limit]
    return [
        {
            "title": r.get("title"),
            "url": r.get("url"),
            "source": (r.get("source") or {}).get("title"),
            "published_at": r.get("published_at"),
            "currencies": [c.get("code") for c in (r.get("currencies") or [])],
        }
        for r in results
    ]
