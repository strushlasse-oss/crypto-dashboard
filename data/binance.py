"""Live price feed from Binance public REST API. No API key required."""
from __future__ import annotations

import json
import ssl
import urllib.request

import streamlit as st

_SSL = ssl.create_default_context()
_SSL.check_hostname = False
_SSL.verify_mode = ssl.CERT_NONE

# Map CoinGecko IDs to Binance symbols.
_SYMBOL_MAP: dict[str, str] = {
    "bitcoin": "BTCUSDT",
    "ethereum": "ETHUSDT",
    "solana": "SOLUSDT",
    "binancecoin": "BNBUSDT",
    "ripple": "XRPUSDT",
    "cardano": "ADAUSDT",
    "dogecoin": "DOGEUSDT",
    "avalanche-2": "AVAXUSDT",
    "chainlink": "LINKUSDT",
    "polkadot": "DOTUSDT",
    "matic-network": "MATICUSDT",
    "uniswap": "UNIUSDT",
    "litecoin": "LTCUSDT",
    "cosmos": "ATOMUSDT",
}

_BASE = "https://api.binance.com/api/v3/ticker/24hr?symbol="


@st.cache_data(ttl=2, show_spinner=False)
def get_live_ticker(coin_id: str) -> dict | None:
    """Return 24h ticker from Binance with 5s cache. Returns None if unsupported."""
    symbol = _SYMBOL_MAP.get(coin_id)
    if not symbol:
        return None
    try:
        with urllib.request.urlopen(f"{_BASE}{symbol}", timeout=3, context=_SSL) as r:
            data = json.loads(r.read())
        return {
            "price": float(data["lastPrice"]),
            "change_pct": float(data["priceChangePercent"]),
        }
    except Exception:
        return None
