"""Liquidation pressure from Binance futures (L/S ratio + OI change)."""
from __future__ import annotations

import json
import ssl
import urllib.request
from datetime import datetime, timezone

import streamlit as st

from data.binance import _SYMBOL_MAP

_SSL = ssl.create_default_context()
_SSL.check_hostname = False
_SSL.verify_mode = ssl.CERT_NONE
_FAPI = "https://fapi.binance.com/fapi/v1"
_FDATA = "https://fapi.binance.com/futures/data"


def _get(url: str) -> list | dict | None:
    try:
        with urllib.request.urlopen(url, timeout=5, context=_SSL) as r:
            return json.loads(r.read())
    except Exception:
        return None


@st.cache_data(ttl=60, show_spinner=False)
def get_liquidation_data(coin_id: str) -> dict | None:
    symbol = _SYMBOL_MAP.get(coin_id)
    if not symbol:
        return None

    ls = _get(f"{_FDATA}/globalLongShortAccountRatio?symbol={symbol}&period=1h&limit=2")
    oi_hist = _get(f"{_FDATA}/openInterestHist?symbol={symbol}&period=1h&limit=2")
    ticker = _get(f"{_FAPI}/ticker/24hr?symbol={symbol}")

    if not ls or not ticker:
        return None

    current_ls  = float(ls[-1]["longShortRatio"])
    prev_ls     = float(ls[0]["longShortRatio"]) if len(ls) > 1 else current_ls
    long_pct    = float(ls[-1]["longAccount"]) * 100
    short_pct   = float(ls[-1]["shortAccount"]) * 100

    oi_change_pct = None
    if oi_hist and len(oi_hist) >= 2:
        oi_now  = float(oi_hist[-1]["sumOpenInterest"])
        oi_prev = float(oi_hist[0]["sumOpenInterest"])
        if oi_prev > 0:
            oi_change_pct = (oi_now - oi_prev) / oi_prev * 100

    price_change = float(ticker.get("priceChangePercent", 0))

    # Estimate dominant liquidation side
    if price_change < -1.5 and oi_change_pct is not None and oi_change_pct < -0.5:
        pressure = "longs"
    elif price_change > 1.5 and oi_change_pct is not None and oi_change_pct < -0.5:
        pressure = "shorts"
    else:
        pressure = "neutral"

    return {
        "symbol":       symbol,
        "long_pct":     long_pct,
        "short_pct":    short_pct,
        "ls_ratio":     current_ls,
        "oi_change":    oi_change_pct,
        "price_change": price_change,
        "pressure":     pressure,
    }
