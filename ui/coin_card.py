"""Per-coin detail view: bias boxes + AI overview + price card + status cards + chart."""
from __future__ import annotations

import streamlit as st

from analysis import ai_overview
from analysis import edge_factor as ef
from analysis import indicators as ind
from data import coingecko as cg
from data import cme_gaps as cme
from ui import bearing_card, derivatives_charts, edge_score, flow_card, price_card, status_cards, tradingview
from ui.styles import GREEN, RED, YELLOW, TEXT_DIM, TEXT_MUTED, ACCENT


def _render_rsi_scale(rsi_val: float | None) -> None:
    """RSI on a real 0–100 scale with oversold/neutral/overbought zones."""
    st.markdown("<div class='pcard-title'>RSI · 0–100 Skala</div>", unsafe_allow_html=True)
    if rsi_val is None:
        st.markdown("<div class='pcard-sub'>Kein RSI verfügbar.</div>", unsafe_allow_html=True)
        return

    rsi = float(rsi_val)
    if rsi < 30:
        zone, zone_color = "Überverkauft", RED
    elif rsi > 70:
        zone, zone_color = "Überkauft", RED
    elif 45 <= rsi <= 60:
        zone, zone_color = "Sweet-Spot", GREEN
    else:
        zone, zone_color = "Neutral", YELLOW

    pos_pct = min(100, max(0, rsi))

    st.markdown(
        f"<div style='display:flex;justify-content:space-between;align-items:baseline;margin-bottom:0.4rem'>"
        f"<span style='font-size:1.6rem;font-weight:700;color:{zone_color}'>{rsi:.1f}</span>"
        f"<span class='pill' style='background:rgba({_zone_rgb(zone_color)},0.12);"
        f"color:{zone_color};border:1px solid rgba({_zone_rgb(zone_color)},0.3)'>{zone}</span>"
        f"</div>"
        # gradient bar: red → yellow → green → yellow → red
        f"<div style='position:relative;margin-bottom:0.3rem'>"
        f"<div style='height:10px;border-radius:5px;background:"
        f"linear-gradient(90deg,{RED} 0%,{YELLOW} 20%,{GREEN} 35%,{GREEN} 65%,{YELLOW} 80%,{RED} 100%)'></div>"
        f"<div style='position:absolute;top:-3px;left:{pos_pct:.1f}%;transform:translateX(-50%)'>"
        f"<div style='width:16px;height:16px;border-radius:50%;"
        f"background:white;border:2px solid {zone_color};box-shadow:0 0 10px {zone_color}'></div>"
        f"</div></div>"
        f"<div style='display:flex;justify-content:space-between;font-size:0.7rem;color:{TEXT_MUTED}'>"
        f"<span>0 · Überverkauft</span><span>30</span><span>45–60 Sweet-Spot</span><span>70</span><span>100 · Überkauft</span>"
        f"</div>",
        unsafe_allow_html=True,
    )


def _zone_rgb(hex_color: str) -> str:
    h = hex_color.lstrip("#")
    return f"{int(h[0:2],16)},{int(h[2:4],16)},{int(h[4:6],16)}"


def _header(coin: dict, market: dict) -> None:
    name = coin.get("name") or market.get("name", coin["id"])
    symbol = (coin.get("symbol") or market.get("symbol", "")).upper()
    tag = coin.get("tag", "")
    image = market.get("image", "")
    tag_html = f"<span class='coin-tag'>{tag}</span>" if tag else ""
    st.markdown(
        f"<div class='coin-head'>"
        f"{f'<img src=\"{image}\"/>' if image else ''}"
        f"<div>"
        f"<div class='coin-name'>{name} {tag_html}</div>"
        f"<div class='coin-ticker'>{symbol} · CoinGecko · TradingView</div>"
        f"</div></div>",
        unsafe_allow_html=True,
    )


def _bias_boxes(edge, struct: dict, fng_val: int | None) -> None:
    """HybridTrader-style: Bias · Technical · AI Confidence as 3 boxes."""
    if edge is None:
        return

    # Bias
    if edge.label == "strong":
        bias_val, bias_color = "Bullish", GREEN
    elif edge.label == "low":
        bias_val, bias_color = "Bearish", RED
    else:
        bias_val, bias_color = "Neutral", YELLOW

    # Technical
    tech_label = struct.get("label", "–")
    tech_klass = struct.get("klass", "pill-dim")
    tech_color = GREEN if "green" in tech_klass else (RED if "red" in tech_klass else YELLOW)

    # AI Confidence (derived from edge score)
    conf = edge.score

    st.markdown(
        f"<div class='bias-grid'>"
        # Box 1 – Bias
        f"<div class='bias-box'>"
        f"<div class='bias-box-label'>Bias</div>"
        f"<div class='bias-box-value' style='color:{bias_color}'>{bias_val}</div>"
        f"<div class='bias-conf-bar'>"
        f"<div class='bias-conf-fill' style='width:{conf}%;background:{bias_color}'></div>"
        f"</div></div>"
        # Box 2 – Technical
        f"<div class='bias-box'>"
        f"<div class='bias-box-label'>Technical</div>"
        f"<div class='bias-box-value' style='color:{tech_color}'>{tech_label}</div>"
        f"<div class='bias-conf-bar'>"
        f"<div class='bias-conf-fill' style='width:{conf}%;background:{tech_color}'></div>"
        f"</div></div>"
        # Box 3 – AI Confidence
        f"<div class='bias-box'>"
        f"<div class='bias-box-label'>AI Confidence</div>"
        f"<div class='bias-box-value' style='color:{ACCENT}'>{conf}%</div>"
        f"<div class='bias-conf-bar'>"
        f"<div class='bias-conf-fill' style='width:{conf}%;background:{ACCENT}'></div>"
        f"</div></div>"
        f"</div>",
        unsafe_allow_html=True,
    )


def render(coin: dict, market: dict, fear_greed: dict | None, days: int = 90) -> None:
    name = coin.get("name") or market.get("name", coin["id"])
    symbol = (coin.get("symbol") or market.get("symbol", "")).upper()

    raw = cg.get_market_chart(coin["id"], days=max(days, 200))
    enriched = ind.compute_indicators(raw) if not raw.empty else raw
    snap = ind.latest_snapshot(enriched) if not enriched.empty else {}
    fng_val = int(fear_greed["value"]) if fear_greed and fear_greed.get("value") else None
    edge = ef.compute(enriched, fng_value=fng_val) if not enriched.empty else None
    struct = status_cards.technical_structure(enriched) if not enriched.empty else {}

    # ── Header ──────────────────────────────────────────────
    head_l, head_r = st.columns([3, 2])
    with head_l:
        _header(coin, market)
    with head_r:
        if edge:
            st.markdown(
                f"<div style='display:flex;align-items:center;gap:0.6rem;padding-top:0.3rem'>"
                f"<span class='pill {'pill-green' if edge.label=='strong' else 'pill-yellow' if edge.label=='mixed' else 'pill-red'}'>"
                f"{edge.headline}</span>"
                f"</div>"
                f"<div class='pcard-sub' style='margin-top:0.45rem;line-height:1.45'>{edge.comment}</div>",
                unsafe_allow_html=True,
            )

    st.write("")

    # ── Bias Boxes ──────────────────────────────────────────
    _bias_boxes(edge, struct, fng_val)

    # ── Price card + AI Overview ─────────────────────────────
    price_col, ai_col = st.columns([1, 1])
    with price_col:
        price_card.render(coin, market)

    with ai_col:
        if edge:
            trend = ind.trend_label(snap) if snap else "unbekannt"
            with st.spinner("Generiere Snapshot…"):
                text, is_ai = ai_overview.snapshot(
                    coin_id=coin["id"], name=name,
                    price=market.get("current_price"),
                    edge=edge, fng_value=fng_val, trend=trend,
                )
            badge = ("pill-green" if is_ai else "pill-dim")
            badge_label = ("AI" if is_ai else "Fallback")
            st.markdown(
                f"<div class='ai-card'>"
                f"<div class='ai-card-header'>⬥ AI Overview"
                f"<span class='pill {badge}' style='font-size:0.68rem;padding:2px 7px'>{badge_label}</span>"
                f"</div>"
                f"<div class='ai-card-body'>{text}</div>"
                f"<div style='margin-top:0.6rem;font-size:0.76rem;color:{TEXT_MUTED}'>Cache 30 min</div>"
                f"</div>",
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                "<div class='ai-card'>"
                "<div class='ai-card-header'>⬥ AI Overview</div>"
                "<div class='ai-card-body' style='opacity:.5'>Keine Daten verfügbar.</div>"
                "</div>",
                unsafe_allow_html=True,
            )

    st.write("")

    # ── Status Cards ─────────────────────────────────────────
    status_cards.render_row(enriched, fng_val)

    st.write("")

    # ── Flow + Bearing ────────────────────────────────────────
    flow_col, bearing_col = st.columns(2)
    with flow_col:
        with st.container(border=True):
            flow_card.render(enriched)
    with bearing_col:
        with st.container(border=True):
            bearing_card.render(enriched, coin["id"])

    st.write("")

    # ── CME Gaps (BTC only) ───────────────────────────────────
    if coin["id"] == "bitcoin":
        current_price = market.get("current_price")
        gaps = cme.get_open_gaps()
        with st.container(border=True):
            st.markdown(
                "<div class='pcard-title' style='margin-bottom:0.5rem'>CME Gaps · Unaufgefüllt</div>",
                unsafe_allow_html=True,
            )
            if not gaps:
                st.markdown(
                    f"<div style='color:{TEXT_DIM};font-size:13px'>Keine offenen CME Gaps gefunden.</div>",
                    unsafe_allow_html=True,
                )
            else:
                above = [g for g in gaps if g["low"] > (current_price or 0)]
                below = [g for g in gaps if g["high"] <= (current_price or 0)]
                rows = ""
                for g in above[:4]:
                    dist = (g["low"] - current_price) / current_price * 100 if current_price else 0
                    rows += (
                        f"<tr>"
                        f"<td style='padding:6px 10px;color:#e0e0e0;font-weight:600'>"
                        f"${g['low']:,.0f} – ${g['high']:,.0f}</td>"
                        f"<td style='padding:6px 10px;color:{RED};font-size:12px'>"
                        f"▲ +{dist:.1f}% entfernt</td>"
                        f"<td style='padding:6px 10px;color:rgba(255,255,255,0.4);font-size:12px'>"
                        f"{g['size_pct']:+.2f}% Gap · {g['date']}</td>"
                        f"</tr>"
                    )
                for g in below[:4]:
                    dist = (current_price - g["high"]) / current_price * 100 if current_price else 0
                    rows += (
                        f"<tr>"
                        f"<td style='padding:6px 10px;color:#e0e0e0;font-weight:600'>"
                        f"${g['low']:,.0f} – ${g['high']:,.0f}</td>"
                        f"<td style='padding:6px 10px;color:{GREEN};font-size:12px'>"
                        f"▼ -{dist:.1f}% entfernt</td>"
                        f"<td style='padding:6px 10px;color:rgba(255,255,255,0.4);font-size:12px'>"
                        f"{g['size_pct']:+.2f}% Gap · {g['date']}</td>"
                        f"</tr>"
                    )
                st.markdown(
                    f"<table style='width:100%;border-collapse:collapse;font-size:13px;font-family:Inter,sans-serif'>"
                    f"<thead><tr style='border-bottom:1px solid rgba(255,255,255,0.08)'>"
                    f"<th style='padding:4px 10px;text-align:left;font-size:10px;text-transform:uppercase;"
                    f"letter-spacing:0.1em;color:rgba(255,255,255,0.3);font-weight:600'>Preis-Range</th>"
                    f"<th style='padding:4px 10px;text-align:left;font-size:10px;text-transform:uppercase;"
                    f"letter-spacing:0.1em;color:rgba(255,255,255,0.3);font-weight:600'>Abstand</th>"
                    f"<th style='padding:4px 10px;text-align:left;font-size:10px;text-transform:uppercase;"
                    f"letter-spacing:0.1em;color:rgba(255,255,255,0.3);font-weight:600'>Info</th>"
                    f"</tr></thead><tbody>{rows}</tbody></table>",
                    unsafe_allow_html=True,
                )
                st.markdown(
                    f"<div style='font-size:11px;color:{TEXT_DIM};margin-top:0.4rem'>"
                    f"{len(above)} Gap(s) über Kurs · {len(below)} Gap(s) unter Kurs · "
                    f"Quelle: CME BTC Futures (BTC=F)</div>",
                    unsafe_allow_html=True,
                )

    st.write("")

    # ── CVD / OI / Funding Rates ──────────────────────────────
    st.markdown(
        "<div class='pcard-title' style='margin-bottom:0.6rem'>"
        "Marktstruktur · CVD · Open Interest · Funding Rate</div>",
        unsafe_allow_html=True,
    )
    derivatives_charts.render(coin["id"])

    # ── TradingView Chart ────────────────────────────────────
    st.markdown(
        f"<div class='pcard-title' style='margin-top:1.2rem'>Chart</div>",
        unsafe_allow_html=True,
    )
    tv_symbol = coin.get("tv") or f"BINANCE:{symbol}USDT"
    tradingview.render(tv_symbol, height=600, container_id=f"tv_{coin['id']}")

    if snap:
        st.session_state[f"snap_{coin['id']}"] = snap
        st.session_state[f"trend_{coin['id']}"] = ind.trend_label(snap)
    if edge:
        st.session_state[f"edge_{coin['id']}"] = edge
