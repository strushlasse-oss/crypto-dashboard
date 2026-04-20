"""Landing view: sessions, capital flow, and coin cards."""
from __future__ import annotations

from typing import Any

import streamlit as st

from analysis import edge_factor as ef
from analysis import indicators as ind
from data import binance as bnb
from data import coingecko as cg
from data import global_metrics as gm
from ui import ai_summary_widget, capital_flow, market_sessions, metrics_bar, status_cards, telegram_widget, liquidations_widget
from ui.styles import GREEN, RED, TEXT_DIM, TEXT_MUTED, ACCENT


def _render_calendar() -> None:
    from datetime import timezone as _tz
    st.markdown("<div class='pcard-title' style='margin-bottom:0.6rem'>Economic Calendar · High Impact</div>",
                unsafe_allow_html=True)
    events = gm.get_calendar(impact_filter="High")
    if not events:
        st.markdown(f"<div style='color:{TEXT_DIM};font-size:13px'>Keine Daten verfügbar.</div>",
                    unsafe_allow_html=True)
        return

    rows = ""
    shown = 0
    for e in events:
        diff = e["diff_sec"]
        if diff < -3600:
            continue
        time_str = e["date"].strftime("%a %d. %b  %H:%M UTC")
        if diff > 0:
            h, m = int(diff // 3600), int((diff % 3600) // 60)
            countdown = f"in {h}h {m}m" if h else f"in {m}m"
            cd_color = "#f7a832" if diff < 7200 else "rgba(255,255,255,0.35)"
        else:
            countdown = "läuft"
            cd_color = "#ff4455"
        forecast = e.get("forecast") or "–"
        previous = e.get("previous") or "–"
        actual   = e.get("actual") or ""
        actual_html = f"<span style='color:#00d084;font-weight:700'>{actual}</span>" if actual else ""
        rows += (
            f"<tr>"
            f"<td style='padding:7px 10px;color:#e0e0e0;font-weight:600'>{e['title']}"
            f" <span style='color:rgba(255,255,255,0.3);font-size:11px'>({e['country']})</span></td>"
            f"<td style='padding:7px 10px;color:rgba(255,255,255,0.45);font-size:12px'>{time_str}</td>"
            f"<td style='padding:7px 10px;font-weight:700;color:{cd_color}'>{countdown}</td>"
            f"<td style='padding:7px 10px;color:rgba(255,255,255,0.45);font-size:12px'>{forecast}</td>"
            f"<td style='padding:7px 10px;color:rgba(255,255,255,0.45);font-size:12px'>{previous}</td>"
            f"<td style='padding:7px 10px;font-size:12px'>{actual_html}</td>"
            f"</tr>"
        )
        shown += 1
        if shown >= 8:
            break

    if shown == 0:
        st.markdown(f"<div style='color:{TEXT_DIM};font-size:13px'>Keine anstehenden Ereignisse.</div>",
                    unsafe_allow_html=True)
        return

    st.markdown(
        f"<table style='width:100%;border-collapse:collapse;font-size:13px;font-family:Inter,sans-serif'>"
        f"<thead><tr style='border-bottom:1px solid rgba(255,255,255,0.08)'>"
        f"<th style='padding:4px 10px;text-align:left;font-size:10px;text-transform:uppercase;"
        f"letter-spacing:0.1em;color:rgba(255,255,255,0.3);font-weight:600'>Ereignis</th>"
        f"<th style='padding:4px 10px;text-align:left;font-size:10px;text-transform:uppercase;"
        f"letter-spacing:0.1em;color:rgba(255,255,255,0.3);font-weight:600'>Zeit</th>"
        f"<th style='padding:4px 10px;text-align:left;font-size:10px;text-transform:uppercase;"
        f"letter-spacing:0.1em;color:rgba(255,255,255,0.3);font-weight:600'>Countdown</th>"
        f"<th style='padding:4px 10px;text-align:left;font-size:10px;text-transform:uppercase;"
        f"letter-spacing:0.1em;color:rgba(255,255,255,0.3);font-weight:600'>Prognose</th>"
        f"<th style='padding:4px 10px;text-align:left;font-size:10px;text-transform:uppercase;"
        f"letter-spacing:0.1em;color:rgba(255,255,255,0.3);font-weight:600'>Vorher</th>"
        f"<th style='padding:4px 10px;text-align:left;font-size:10px;text-transform:uppercase;"
        f"letter-spacing:0.1em;color:rgba(255,255,255,0.3);font-weight:600'>Aktuell</th>"
        f"</tr></thead>"
        f"<tbody>{rows}</tbody></table>",
        unsafe_allow_html=True,
    )


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

    # Economic Calendar
    st.markdown("<div style='height:1.2rem'></div>", unsafe_allow_html=True)
    with st.container(border=True):
        _render_calendar()

