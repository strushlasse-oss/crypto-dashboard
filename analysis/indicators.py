"""Technical indicators computed from CoinGecko market-chart data.

Uses pandas-ta-classic; real import path is `pandas_ta_classic`.
"""
from __future__ import annotations

import numpy as np
import pandas as pd
import pandas_ta_classic as ta


def compute_indicators(df: pd.DataFrame) -> pd.DataFrame:
    """Attach RSI, MACD, SMA 50/200 and Bollinger Bands to a close-price df.

    Expects columns: time, close (volume optional). Returns a copy.
    """
    if df.empty or "close" not in df.columns:
        return df.copy()

    out = df.copy().reset_index(drop=True)
    close = out["close"]

    out["rsi_14"] = ta.rsi(close, length=14)
    out["sma_50"] = ta.sma(close, length=50)
    out["sma_200"] = ta.sma(close, length=200)

    macd = ta.macd(close, fast=12, slow=26, signal=9)
    if macd is not None and not macd.empty:
        out["macd"] = macd.iloc[:, 0]
        out["macd_hist"] = macd.iloc[:, 1]
        out["macd_signal"] = macd.iloc[:, 2]

    bb = ta.bbands(close, length=20, std=2)
    if bb is not None and not bb.empty:
        out["bb_lower"] = bb.iloc[:, 0]
        out["bb_mid"] = bb.iloc[:, 1]
        out["bb_upper"] = bb.iloc[:, 2]

    return out


def latest_snapshot(df: pd.DataFrame) -> dict:
    """Extract the most recent row of indicators as a flat dict for Claude prompts."""
    if df.empty:
        return {}
    last = df.iloc[-1]
    keys = ["close", "rsi_14", "sma_50", "sma_200", "macd", "macd_signal",
            "macd_hist", "bb_lower", "bb_mid", "bb_upper", "volume"]
    snap: dict = {}
    for k in keys:
        if k in df.columns:
            v = last[k]
            snap[k] = None if pd.isna(v) else float(v)
    return snap


def trend_label(snap: dict) -> str:
    """Cheap, deterministic trend tag used alongside indicator values."""
    close = snap.get("close")
    sma50 = snap.get("sma_50")
    sma200 = snap.get("sma_200")
    if not all(isinstance(x, (int, float)) and not np.isnan(x) for x in [close, sma50, sma200] if x is not None):
        return "unbekannt"
    if close is None or sma50 is None or sma200 is None:
        return "unbekannt"
    if close > sma50 > sma200:
        return "Aufwärtstrend"
    if close < sma50 < sma200:
        return "Abwärtstrend"
    return "Seitwärts / gemischt"
