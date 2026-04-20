"""CVD, Open Interest and Funding Rates from Binance (spot + futures). No API key needed."""
from __future__ import annotations

import json
import ssl
import urllib.request
from datetime import datetime, timezone

_SSL = ssl.create_default_context()
_SSL.check_hostname = False
_SSL.verify_mode = ssl.CERT_NONE

import pandas as pd
import streamlit as st

from data.binance import _SYMBOL_MAP

_SPOT  = "https://api.binance.com/api/v3/klines"
_FAPI  = "https://fapi.binance.com/fapi/v1"
_FDATA = "https://fapi.binance.com/futures/data"

_INTERVALS = {"1h": "1h", "4h": "4h", "1d": "1d"}


def _get(url: str, timeout: int = 5) -> list | dict | None:
    try:
        with urllib.request.urlopen(url, timeout=timeout, context=_SSL) as r:
            return json.loads(r.read())
    except Exception:
        return None


# ── CVD ────────────────────────────────────────────────────────────────────────

@st.cache_data(ttl=60, show_spinner=False)
def get_cvd(coin_id: str, interval: str = "1h", limit: int = 96) -> pd.DataFrame:
    """Cumulative Volume Delta from Binance spot klines (taker buy vs sell)."""
    symbol = _SYMBOL_MAP.get(coin_id)
    if not symbol:
        return pd.DataFrame()

    data = _get(f"{_SPOT}?symbol={symbol}&interval={interval}&limit={limit}")
    if not data:
        return pd.DataFrame()

    rows = []
    for k in data:
        ts   = int(k[0])
        vol  = float(k[5])
        buy  = float(k[9])
        sell = vol - buy
        rows.append({
            "time":  datetime.fromtimestamp(ts / 1000, tz=timezone.utc),
            "buy":   buy,
            "sell":  sell,
            "delta": buy - sell,
        })

    df = pd.DataFrame(rows)
    df["cvd"] = df["delta"].cumsum()
    return df


# ── Open Interest ──────────────────────────────────────────────────────────────

@st.cache_data(ttl=300, show_spinner=False)
def get_open_interest(coin_id: str, period: str = "1h", limit: int = 96) -> pd.DataFrame:
    """Open Interest history from Binance Futures."""
    symbol = _SYMBOL_MAP.get(coin_id)
    if not symbol:
        return pd.DataFrame()

    data = _get(f"{_FDATA}/openInterestHist?symbol={symbol}&period={period}&limit={limit}")
    if not data:
        return pd.DataFrame()

    rows = []
    for d in data:
        rows.append({
            "time": datetime.fromtimestamp(int(d["timestamp"]) / 1000, tz=timezone.utc),
            "oi":   float(d["sumOpenInterest"]),
            "oi_usd": float(d["sumOpenInterestValue"]),
        })
    return pd.DataFrame(rows)


# ── Funding Rate ───────────────────────────────────────────────────────────────

@st.cache_data(ttl=300, show_spinner=False)
def get_funding_rate(coin_id: str, limit: int = 96) -> pd.DataFrame:
    """Funding rate history from Binance Futures."""
    symbol = _SYMBOL_MAP.get(coin_id)
    if not symbol:
        return pd.DataFrame()

    data = _get(f"{_FAPI}/fundingRate?symbol={symbol}&limit={limit}")
    if not data:
        return pd.DataFrame()

    rows = []
    for d in data:
        rate = float(d["fundingRate"]) * 100  # convert to %
        rows.append({
            "time": datetime.fromtimestamp(int(d["fundingTime"]) / 1000, tz=timezone.utc),
            "rate": rate,
        })
    return pd.DataFrame(rows)
