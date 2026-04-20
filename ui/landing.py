"""Landing view: sessions, capital flow, and coin cards."""
from __future__ import annotations

from typing import Any

import streamlit as st

from analysis import edge_factor as ef
from analysis import indicators as ind
from data import binance as bnb
from data import coingecko as cg
from ui import ai_summary_widget, capital_flow, market_sessions, metrics_bar, status_cards, telegram_widget, liquidations_widget
from ui.styles import GREEN, RED, TEXT_DIM, TEXT_MUTED, ACCENT


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


def _bias_label(edge) -> tuple[str, str]:
    """Returns (label, color) for the bias box."""
    if edge is None:
        return "–", TEXT_DIM
    if edge.label == "strong":
        return "Bullish", GREEN
    if edge.label == "low":
        return "Bearish", RED
    return "Neutral", "#f5c542"


@st.fragment(run_every=2)
def _live_landing_price(coin_id: str, fallback_price: float | None, fallback_change: float | None) -> None:
    ticker = bnb.get_live_ticker(coin_id)
    if ticker:
        p, ch = ticker["price"], ticker["change_pct"]
    else:
        p, ch = fallback_price, fallback_change

    prev_key = f"_prev_price_{coin_id}"
    prev = st.session_state.get(prev_key)
    if p is not None:
        tick_cls = "price-tick-down" if (prev is not None and p < prev) else "price-tick-up"
        st.session_state[prev_key] = p
    else:
        tick_cls = "price-tick-up"

    color = GREEN if (ch or 0) >= 0 else RED
    st.markdown(
        f"<div class='price-main' style='font-size:1.75rem'>"
        f"<span class='{tick_cls}'>{_fmt_usd(p)}</span></div>"
        f"<div style='color:{color};font-weight:600;font-size:0.9rem;margin-top:0.15rem'>"
        f"{_fmt_pct(ch)} <span style='color:{TEXT_DIM};font-weight:400'>· 24h</span></div>",
        unsafe_allow_html=True,
    )


def render(coins: list[dict], markets_by_id: dict[str, dict],
           fng_value: int | None) -> None:
    # Coin cards row
    st.markdown(
        f"<div style='font-size:0.72rem;text-transform:uppercase;letter-spacing:0.1em;"
        f"color:{TEXT_MUTED};font-weight:600;margin-bottom:0.6rem'>AI Macro Desk</div>",
        unsafe_allow_html=True,
    )

    all_markets = []

    # Pre-load all market data
    coin_data = []
    for coin in coins:
        m = markets_by_id.get(coin["id"], {})
        all_markets.append(m)
        raw = cg.get_market_chart(coin["id"], days=200)
        edge = None
        if not raw.empty:
            enriched = ind.compute_indicators(raw)
            edge = ef.compute(enriched, fng_value=fng_value)
        coin_data.append((coin, m, edge))

    # Coin switcher — radio buttons styled as pills
    symbols = [(coin.get("symbol") or coin["id"]).upper() for coin, _, _ in coin_data]
    selected_idx = st.session_state.get("_landing_coin_idx", 0)

    btn_cols = st.columns(len(coin_data))
    for i, (col, sym) in enumerate(zip(btn_cols, symbols)):
        chg = coin_data[i][1].get("price_change_percentage_24h_in_currency") or 0
        arrow = "▲" if chg >= 0 else "▼"
        chg_color = GREEN if chg >= 0 else RED
        is_sel = i == selected_idx
        label = f"{sym}"
        with col:
            if st.button(
                label,
                key=f"_coin_sel_{i}",
                type="primary" if is_sel else "secondary",
                use_container_width=True,
            ):
                st.session_state["_landing_coin_idx"] = i
                st.rerun()

    coin, m, edge = coin_data[selected_idx]
    bias_label_val, bias_color = _bias_label(edge)
    confidence = edge.score if edge else 0
    name   = coin.get("name", coin["id"])
    symbol = (coin.get("symbol") or "").upper()
    tag    = coin.get("tag", "")
    image  = m.get("image", "")

    st.markdown("<div style='height:0.4rem'></div>", unsafe_allow_html=True)
    with st.container(border=True):
        st.markdown(
            f"<div class='coin-head' style='margin-bottom:0.7rem'>"
            f"{f'<img src=\"{image}\" style=\"width:36px;height:36px\"/>' if image else ''}"
            f"<div>"
            f"<div class='coin-name' style='font-size:1.15rem'>{name}</div>"
            f"<div class='coin-ticker'>{symbol} · {tag}</div>"
            f"</div></div>",
            unsafe_allow_html=True,
        )

        _live_landing_price(
            coin["id"],
            m.get("current_price"),
            m.get("price_change_percentage_24h_in_currency"),
        )

        st.markdown(
            f"<div style='margin-top:0.8rem;padding-top:0.7rem;"
            f"border-top:1px solid rgba(255,255,255,0.06)'>"
            f"<div style='display:flex;align-items:center;justify-content:space-between;margin-bottom:0.4rem'>"
            f"<span style='font-size:0.7rem;text-transform:uppercase;letter-spacing:0.1em;"
            f"color:{TEXT_MUTED};font-weight:600'>Bias</span>"
            f"<span style='font-size:1.05rem;font-weight:700;color:{bias_color}'>{bias_label_val}</span>"
            f"</div>"
            f"<div style='font-size:0.7rem;text-transform:uppercase;letter-spacing:0.1em;"
            f"color:{TEXT_MUTED};font-weight:600;margin-bottom:0.3rem'>AI Confidence · {confidence}%</div>"
            f"<div style='background:rgba(255,255,255,0.07);height:4px;border-radius:2px;overflow:hidden'>"
            f"<div style='width:{confidence}%;height:100%;background:{bias_color}'></div>"
            f"</div></div>",
            unsafe_allow_html=True,
        )

        if st.button("Öffnen →", key=f"open_{coin['id']}", use_container_width=True):
            st.session_state["selected_coin"] = coin["id"]
            st.rerun()

    # Metrics bar below coin cards
    st.markdown("<div style='height:0.4rem'></div>", unsafe_allow_html=True)
    metrics_bar.render(fng_value=fng_value)

    # AI summary + Sessions side by side
    ai_col, sess_col = st.columns([1, 1])
    with ai_col:
        ai_summary_widget.render()
    with sess_col:
        market_sessions.render()

    # Capital Flow + WatcherGuru Feed + Liquidations
    st.markdown("<div style='height:1.2rem'></div>", unsafe_allow_html=True)
    flow_col, tg_col, liq_col = st.columns([1, 1, 1])

    with flow_col:
        with st.container(border=True):
            capital_flow.render(all_markets)

    with tg_col:
        with st.container(border=True):
            telegram_widget.render()

    with liq_col:
        with st.container(border=True):
            liquidations_widget.render()

