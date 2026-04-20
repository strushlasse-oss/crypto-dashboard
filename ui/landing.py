"""Landing view: sessions, capital flow, and coin cards."""
from __future__ import annotations

from typing import Any

import plotly.graph_objects as go
import streamlit as st

from analysis import ai_overview
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

    import pandas as _pd

    all_markets = []
    selected_idx = st.session_state.get("_landing_coin_idx", 0)

    # Load chart data only for the selected coin to avoid rate-limit spam
    coin_data = []
    for i, coin in enumerate(coins):
        m = markets_by_id.get(coin["id"], {})
        all_markets.append(m)
        if i == selected_idx:
            raw = cg.get_market_chart(coin["id"], days=200)
            edge, enriched, snap = None, raw, {}
            if not raw.empty:
                enriched = ind.compute_indicators(raw)
                edge = ef.compute(enriched, fng_value=fng_value)
                snap = ind.latest_snapshot(enriched)
        else:
            edge, enriched, snap = None, _pd.DataFrame(), {}
        coin_data.append((coin, m, edge, enriched, snap))

    coin, m, edge, enriched, snap = coin_data[selected_idx]
    bias_label_val, bias_color = _bias_label(edge)
    confidence = edge.score if edge else 0
    name   = coin.get("name", coin["id"])
    symbol = (coin.get("symbol") or "").upper()
    tag    = coin.get("tag", "")
    image  = m.get("image", "")

    st.markdown("<div style='height:0.4rem'></div>", unsafe_allow_html=True)
    with st.container(border=True):
        left_col, right_col = st.columns([1, 1])

        with left_col:
            # Coin switcher above price
            syms = [(c.get("symbol") or c["id"]).upper() for (c, *_) in coin_data]
            chosen = st.segmented_control(
                "Coin",
                options=syms,
                default=syms[selected_idx],
                label_visibility="collapsed",
                key="_coin_seg",
            )
            if chosen and syms.index(chosen) != selected_idx:
                st.session_state["_landing_coin_idx"] = syms.index(chosen)
                st.rerun()

            st.markdown("<div style='height:0.3rem'></div>", unsafe_allow_html=True)

            # Coin header
            st.markdown(
                f"<div class='coin-head' style='margin-bottom:0.5rem'>"
                f"{f'<img src=\"{image}\" style=\"width:32px;height:32px\"/>' if image else ''}"
                f"<div>"
                f"<div class='coin-name' style='font-size:1.05rem'>{name}</div>"
                f"<div class='coin-ticker'>{symbol} · {tag}</div>"
                f"</div></div>",
                unsafe_allow_html=True,
            )

            # Live price
            _live_landing_price(
                coin["id"],
                m.get("current_price"),
                m.get("price_change_percentage_24h_in_currency"),
            )

            # Mini price chart (30 days)
            if not enriched.empty and "close" in enriched.columns:
                prices = enriched["close"].dropna().tail(30).tolist()
                if len(prices) >= 2:
                    chg_color_val = GREEN if (prices[-1] >= prices[0]) else RED
                    lo, hi = min(prices), max(prices)
                    pad = (hi - lo) * 0.05 or 1
                    fig = go.Figure(go.Scatter(
                        y=prices, mode="lines",
                        line=dict(color=chg_color_val, width=1.5),
                        fill="tozeroy",
                        fillcolor=f"rgba({'0,208,132' if chg_color_val==GREEN else '255,68,85'},0.08)",
                        hoverinfo="skip",
                    ))
                    fig.update_layout(
                        margin=dict(l=0, r=0, t=4, b=0), height=80,
                        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                        xaxis=dict(visible=False), yaxis=dict(visible=False, range=[lo-pad, hi+pad]),
                    )
                    st.plotly_chart(fig, use_container_width=True,
                                   config={"displayModeBar": False},
                                   key=f"mini_chart_{coin['id']}")

        with right_col:
            st.markdown("<div style='height:2.8rem'></div>", unsafe_allow_html=True)
            st.markdown(
                f"<div style='padding-left:1rem;border-left:1px solid rgba(255,255,255,0.06)'>"
                f"<div style='display:flex;align-items:center;justify-content:space-between;margin-bottom:0.5rem'>"
                f"<span style='font-size:0.7rem;text-transform:uppercase;letter-spacing:0.1em;"
                f"color:{TEXT_MUTED};font-weight:600'>Bias</span>"
                f"<span style='font-size:1.2rem;font-weight:700;color:{bias_color}'>{bias_label_val}</span>"
                f"</div>"
                f"<div style='font-size:0.7rem;text-transform:uppercase;letter-spacing:0.1em;"
                f"color:{TEXT_MUTED};font-weight:600;margin-bottom:0.3rem'>AI Confidence · {confidence}%</div>"
                f"<div style='background:rgba(255,255,255,0.07);height:4px;border-radius:2px;overflow:hidden;margin-bottom:0.8rem'>"
                f"<div style='width:{confidence}%;height:100%;background:{bias_color}'></div>"
                f"</div></div>",
                unsafe_allow_html=True,
            )

            # Per-coin AI overview
            if edge:
                trend = ind.trend_label(snap) if snap else "unbekannt"
                ai_text, is_ai = ai_overview.snapshot(
                    coin_id=coin["id"], name=name,
                    price=m.get("current_price"),
                    edge=edge, fng_value=fng_value, trend=trend,
                )
                safe = ai_text.replace("<", "&lt;").replace(">", "&gt;")
                badge = "rgba(0,208,132,0.15)" if is_ai else "rgba(255,255,255,0.06)"
                badge_txt = "AI" if is_ai else "Fallback"
                st.markdown(
                    f"<div style='padding-left:1rem;border-left:1px solid rgba(255,255,255,0.06)'>"
                    f"<div style='display:inline-block;background:{badge};color:{'#00d084' if is_ai else '#888'};"
                    f"border-radius:4px;font-size:9px;font-weight:700;letter-spacing:0.08em;"
                    f"padding:2px 6px;text-transform:uppercase;margin-bottom:6px'>⚡ {badge_txt}</div>"
                    f"<div style='font-size:12.5px;line-height:1.55;color:#c8c8c8'>{safe}</div>"
                    f"</div>",
                    unsafe_allow_html=True,
                )
            elif m.get("current_price"):
                pct = m.get("price_change_percentage_24h_in_currency") or 0
                direction = "gestiegen" if pct >= 0 else "gefallen"
                pct_color = GREEN if pct >= 0 else RED
                st.markdown(
                    f"<div style='padding-left:1rem;border-left:1px solid rgba(255,255,255,0.06)'>"
                    f"<div style='font-size:12.5px;line-height:1.55;color:#888'>"
                    f"{name} ist in den letzten 24h um "
                    f"<span style='color:{pct_color};font-weight:600'>{abs(pct):.2f}%</span> {direction}. "
                    f"Indikatoren werden beim nächsten Reload berechnet.</div>"
                    f"</div>",
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

