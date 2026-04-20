"""Premium price card: big price, 24h change, sparkline, timeframe switcher."""
from __future__ import annotations

from typing import Any

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from data import binance as bnb
from data import coingecko as cg
from ui.styles import GREEN, RED, TEXT_DIM

TIMEFRAMES = {
    "1D": 1,
    "5D": 5,
    "1M": 30,
    "3M": 90,
    "1Y": 365,
}


def _fmt_pct(v: Any) -> str:
    if v is None:
        return "–"
    try:
        v = float(v)
    except (TypeError, ValueError):
        return "–"
    arrow = "▲" if v >= 0 else "▼"
    return f"{arrow} {v:+.2f}%"


def _fmt_usd(v: Any) -> str:
    if v is None:
        return "–"
    try:
        v = float(v)
    except (TypeError, ValueError):
        return "–"
    if abs(v) >= 1000:
        return f"${v:,.2f}"
    if abs(v) >= 1:
        return f"${v:.2f}"
    return f"${v:.4f}"


def _sparkline(prices: pd.Series, color: str, height: int = 90) -> go.Figure:
    fig = go.Figure(go.Scatter(
        x=list(range(len(prices))), y=prices,
        mode="lines",
        line=dict(color=color, width=2),
        fill="tozeroy",
        fillcolor=f"rgba({_hex_rgb(color)}, 0.12)",
        hoverinfo="skip",
    ))
    y_min, y_max = float(prices.min()), float(prices.max())
    pad = (y_max - y_min) * 0.05 or 1
    fig.update_layout(
        margin=dict(l=0, r=0, t=0, b=0),
        height=height,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        xaxis=dict(visible=False),
        yaxis=dict(visible=False, range=[y_min - pad, y_max + pad]),
    )
    return fig


def _hex_rgb(hex_color: str) -> str:
    h = hex_color.lstrip("#")
    return f"{int(h[0:2],16)}, {int(h[2:4],16)}, {int(h[4:6],16)}"


@st.fragment(run_every=2)
def _live_price_fragment(coin_id: str, fallback_price: float | None, fallback_change: float | None) -> None:
    ticker = bnb.get_live_ticker(coin_id)
    if ticker:
        price = ticker["price"]
        change_24h = ticker["change_pct"]
        source = "Binance · live"
    else:
        price = fallback_price
        change_24h = fallback_change
        source = "CoinGecko · ~60s"

    prev_key = f"_prev_price_{coin_id}"
    prev = st.session_state.get(prev_key)
    if price is not None:
        tick_cls = "price-tick-down" if (prev is not None and price < prev) else "price-tick-up"
        st.session_state[prev_key] = price
    else:
        tick_cls = "price-tick-up"

    change_color = GREEN if (change_24h or 0) >= 0 else RED
    st.markdown(
        f"<div class='price-main'><span class='{tick_cls}'>{_fmt_usd(price)}</span></div>"
        f"<div style='color:{change_color};font-weight:600;margin-top:0.2rem'>"
        f"{_fmt_pct(change_24h)}"
        f" <span style='color:{TEXT_DIM};font-weight:400;font-size:0.8rem'>· 24h · {source}</span></div>",
        unsafe_allow_html=True,
    )


def render(coin: dict, market: dict) -> None:
    """Render the price card. Reads ``timeframe`` from session_state per coin."""
    coin_id = coin["id"]
    key = f"tf_{coin_id}"
    if key not in st.session_state:
        st.session_state[key] = "1M"

    days = TIMEFRAMES[st.session_state[key]]
    chart_df = cg.get_market_chart(coin_id, days=days)
    sparkline_color = GREEN
    pct_for_tf = None
    if not chart_df.empty:
        first = float(chart_df["close"].iloc[0])
        last = float(chart_df["close"].iloc[-1])
        if first > 0:
            pct_for_tf = (last - first) / first * 100
            sparkline_color = GREEN if pct_for_tf >= 0 else RED

    with st.container(border=True):
        st.markdown("<div class='pcard-title'>Preis</div>", unsafe_allow_html=True)

        _live_price_fragment(
            coin_id,
            market.get("current_price"),
            market.get("price_change_percentage_24h_in_currency"),
        )

        if not chart_df.empty:
            st.plotly_chart(
                _sparkline(chart_df["close"], sparkline_color),
                width="stretch",
                config={"displayModeBar": False},
                key=f"spark_{coin_id}_{st.session_state[key]}",
            )
            if pct_for_tf is not None:
                color = GREEN if pct_for_tf >= 0 else RED
                st.markdown(
                    f"<div class='pcard-sub'>"
                    f"<span style='color:{color};font-weight:600'>{_fmt_pct(pct_for_tf)}</span>"
                    f" über {st.session_state[key]}"
                    f"</div>",
                    unsafe_allow_html=True,
                )

        st.segmented_control(
            "Zeitrahmen",
            options=list(TIMEFRAMES.keys()),
            default=st.session_state[key],
            key=key,
            label_visibility="collapsed",
        )
