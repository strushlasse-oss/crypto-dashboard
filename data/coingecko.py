"""CoinGecko API client. Free tier, no key required.

Rate limit: ~30 calls/min on the public endpoint. All calls go through
st.cache_data with generous TTLs to stay well under that budget.
"""
from __future__ import annotations

import time
from typing import Any

import pandas as pd
import requests
import streamlit as st

BASE_URL = "https://api.coingecko.com/api/v3"
TIMEOUT = 15

CORE_COINS = [
    {"id": "bitcoin", "symbol": "btc", "name": "Bitcoin",
     "tv": "BINANCE:BTCUSDT", "tag": "Store of Value"},
    {"id": "ethereum", "symbol": "eth", "name": "Ethereum",
     "tv": "BINANCE:ETHUSDT", "tag": "Smart Contracts"},
    {"id": "solana", "symbol": "sol", "name": "Solana",
     "tv": "BINANCE:SOLUSDT", "tag": "Layer 1"},
]


def _get(path: str, params: dict | None = None) -> Any:
    url = f"{BASE_URL}{path}"
    for attempt in range(3):
        resp = requests.get(url, params=params, timeout=TIMEOUT)
        if resp.status_code == 429:
            time.sleep(5 * (attempt + 1))
            continue
        resp.raise_for_status()
        return resp.json()
    resp.raise_for_status()
    return resp.json()


@st.cache_data(ttl=60, show_spinner=False)
def get_markets(coin_ids: list[str], vs_currency: str = "usd") -> list[dict]:
    """Current market snapshot for the given coin ids."""
    if not coin_ids:
        return []
    data = _get(
        "/coins/markets",
        {
            "vs_currency": vs_currency,
            "ids": ",".join(coin_ids),
            "order": "market_cap_desc",
            "per_page": len(coin_ids),
            "page": 1,
            "sparkline": "true",
            "price_change_percentage": "1h,24h,7d,30d",
        },
    )
    return data


@st.cache_data(ttl=300, show_spinner=False)
def get_ohlc(coin_id: str, days: int = 30, vs_currency: str = "usd") -> pd.DataFrame:
    """OHLC candles. CoinGecko granularity: 1-2 → 30m, 3-30 → 4h, 31+ → 4d."""
    data = _get(
        f"/coins/{coin_id}/ohlc",
        {"vs_currency": vs_currency, "days": days},
    )
    if not data:
        return pd.DataFrame(columns=["time", "open", "high", "low", "close"])
    df = pd.DataFrame(data, columns=["time", "open", "high", "low", "close"])
    df["time"] = pd.to_datetime(df["time"], unit="ms")
    return df


@st.cache_data(ttl=900, show_spinner=False)
def get_market_chart(coin_id: str, days: int = 90, vs_currency: str = "usd") -> pd.DataFrame:
    """Historical price + volume. Returns empty DataFrame on any error."""
    _empty = pd.DataFrame(columns=["time", "close", "volume"])
    try:
        data = _get(
            f"/coins/{coin_id}/market_chart",
            {"vs_currency": vs_currency, "days": days},
        )
    except Exception:
        return _empty
    prices = pd.DataFrame(data.get("prices", []), columns=["time", "close"])
    volumes = pd.DataFrame(data.get("total_volumes", []), columns=["time", "volume"])
    if prices.empty:
        return _empty
    df = prices.merge(volumes, on="time", how="left")
    df["time"] = pd.to_datetime(df["time"], unit="ms")
    return df


@st.cache_data(ttl=600, show_spinner=False)
def search_coins(query: str) -> list[dict]:
    if not query or len(query.strip()) < 2:
        return []
    data = _get("/search", {"query": query.strip()})
    return data.get("coins", [])[:15]
