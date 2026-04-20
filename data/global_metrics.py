"""Global crypto market metrics from CoinGecko + ForexFactory calendar."""
from __future__ import annotations

import json
import ssl
import urllib.request
from datetime import datetime, timezone

import streamlit as st

_SSL = ssl.create_default_context()
_SSL.check_hostname = False
_SSL.verify_mode = ssl.CERT_NONE

_CG_GLOBAL = "https://api.coingecko.com/api/v3/global"
_FF_CAL    = "https://nfs.faireconomy.media/ff_calendar_thisweek.json"


def _get(url: str, timeout: int = 6) -> dict | list | None:
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=timeout, context=_SSL) as r:
            return json.loads(r.read())
    except Exception:
        return None


@st.cache_data(ttl=120, show_spinner=False)
def get_global() -> dict:
    raw = _get(_CG_GLOBAL)
    if not raw:
        return {}
    d = raw.get("data", {})
    return {
        "market_cap_usd":   d.get("total_market_cap", {}).get("usd"),
        "market_cap_change": d.get("market_cap_change_percentage_24h_usd"),
        "btc_dominance":    d.get("market_cap_percentage", {}).get("btc"),
        "eth_dominance":    d.get("market_cap_percentage", {}).get("eth"),
        "volume_24h":       d.get("total_volume", {}).get("usd"),
    }


@st.cache_data(ttl=3600, show_spinner=False)
def get_market_cap_history(days: int = 30) -> dict:
    """Returns {mc: [floats], btc_d: [floats]} oldest→newest."""
    mc_url  = f"https://api.coingecko.com/api/v3/global/market_cap_chart?days={days}"
    btc_url = f"https://api.coingecko.com/api/v3/coins/bitcoin/market_chart?vs_currency=usd&days={days}&interval=daily"
    empty = {"mc": [], "btc_d": []}
    mc_raw  = _get(mc_url)
    btc_raw = _get(btc_url)
    if not mc_raw or not btc_raw:
        return empty
    mc_points  = [v for _, v in mc_raw.get("market_cap_usd", [])]
    btc_mc     = [v for _, v in btc_raw.get("market_cap", [])]
    btc_d = []
    for b, t in zip(btc_mc, mc_points):
        btc_d.append(round(b / t * 100, 2) if t else 0)
    return {"mc": mc_points, "btc_d": btc_d}


@st.cache_data(ttl=1800, show_spinner=False)
def get_calendar(impact_filter: str = "High") -> list[dict]:
    raw = _get(_FF_CAL)
    if not raw:
        return []
    events = []
    now = datetime.now(timezone.utc)
    for e in raw:
        if impact_filter and e.get("impact") != impact_filter:
            continue
        try:
            dt = datetime.fromisoformat(e["date"])
            diff = (dt - now).total_seconds()
        except Exception:
            continue
        events.append({
            "title":    e.get("title", ""),
            "country":  e.get("country", ""),
            "date":     dt,
            "diff_sec": diff,
            "impact":   e.get("impact", ""),
            "forecast": e.get("forecast", "–"),
            "previous": e.get("previous", "–"),
            "actual":   e.get("actual", ""),
        })
    events.sort(key=lambda x: x["date"])
    return events
