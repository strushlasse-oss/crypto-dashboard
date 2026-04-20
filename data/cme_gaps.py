"""CME BTC futures gap detection via yfinance (BTC=F).

CME trades Sunday 17:00 CT – Friday 16:00 CT.
Gaps appear between Friday's close and the next session open (Monday).

Fill definition (standard):
  Gap UP   [prev_close → curr_open]: filled when a subsequent candle's Low
            trades back down through prev_close (the bottom of the gap).
  Gap DOWN [curr_open → prev_close]: filled when a subsequent candle's High
            trades back up through prev_close (the top of the gap).
"""
from __future__ import annotations

from datetime import datetime

import pandas as pd
import streamlit as st


@st.cache_data(ttl=3600, show_spinner=False)
def get_open_gaps(lookback_days: int = 730) -> list[dict]:
    """Return list of unfilled CME gaps, sorted by price descending.

    Each dict: {low, high, size_pct, direction, date, age_days}
    """
    try:
        import yfinance as yf
        df = yf.Ticker("BTC=F").history(period=f"{lookback_days}d", interval="1d")
    except Exception:
        return []

    if df.empty or len(df) < 2:
        return []

    df = df.reset_index()
    df["Date"] = pd.to_datetime(df["Date"]).dt.tz_localize(None)

    gaps: list[dict] = []
    for i in range(1, len(df)):
        prev = df.iloc[i - 1]
        curr = df.iloc[i]

        # Only consider Friday → next-session gaps (CME weekend gap)
        if prev["Date"].weekday() != 4:
            continue

        prev_close = float(prev["Close"])
        curr_open  = float(curr["Open"])
        gap_size_pct = (curr_open - prev_close) / prev_close * 100

        if abs(gap_size_pct) < 0.3:
            continue

        direction = "up" if curr_open > prev_close else "down"
        gap_low  = min(prev_close, curr_open)
        gap_high = max(prev_close, curr_open)

        # Check fill: start from candle AFTER the gap candle (j = i+1)
        # Gap UP  → filled when any Low  <= gap_low  (price returned below gap bottom)
        # Gap DOWN→ filled when any High >= gap_high (price returned above gap top)
        filled = False
        for j in range(i + 1, len(df)):
            lo = float(df.iloc[j]["Low"])
            hi = float(df.iloc[j]["High"])
            if direction == "up" and lo <= gap_low:
                filled = True
                break
            if direction == "down" and hi >= gap_high:
                filled = True
                break

        if not filled:
            age_days = (datetime.now() - curr["Date"].to_pydatetime()).days
            gaps.append({
                "date":      curr["Date"].strftime("%d.%m.%Y"),
                "low":       gap_low,
                "high":      gap_high,
                "size_pct":  gap_size_pct,
                "direction": direction,
                "age_days":  age_days,
            })

    gaps.sort(key=lambda g: g["low"], reverse=True)
    return gaps
