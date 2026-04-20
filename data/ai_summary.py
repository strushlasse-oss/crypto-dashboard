"""AI market summary for the last 12h via Claude API."""
from __future__ import annotations

import os

import anthropic
import streamlit as st

from data import binance as bnb
from data import fear_greed as fg
from data import global_metrics as gm
from data import liquidations as liq


def _api_key() -> str | None:
    try:
        return st.secrets["ANTHROPIC_API_KEY"]
    except Exception:
        return os.environ.get("ANTHROPIC_API_KEY")


def _build_context() -> str:
    lines: list[str] = []

    # Global metrics
    glob = gm.get_global()
    if glob:
        mc   = glob.get("market_cap_usd")
        mc_c = glob.get("market_cap_change")
        btcd = glob.get("btc_dominance")
        lines.append(f"Total Market Cap: ${mc/1e12:.2f}T ({mc_c:+.2f}% 24h)" if mc and mc_c else "Total Market Cap: N/A")
        lines.append(f"BTC Dominance: {btcd:.1f}%" if btcd else "BTC Dominance: N/A")

    # Fear & Greed
    try:
        fng_list = fg.get_fear_greed(limit=1)
        fng_val  = int(fng_list[0]["value"]) if fng_list else None
        fng_cls  = fng_list[0].get("value_classification", "") if fng_list else ""
        lines.append(f"Fear & Greed Index: {fng_val} ({fng_cls})" if fng_val else "F&G: N/A")
    except Exception:
        lines.append("F&G: N/A")

    # Coin prices + 24h change
    for coin_id, symbol in [("bitcoin", "BTC"), ("ethereum", "ETH"), ("solana", "SOL")]:
        ticker = bnb.get_live_ticker(coin_id)
        if ticker:
            lines.append(f"{symbol}: ${ticker['price']:,.2f} ({ticker['change_pct']:+.2f}% 24h)")

    # Liquidation pressure
    for coin_id, symbol in [("bitcoin", "BTC"), ("ethereum", "ETH"), ("solana", "SOL")]:
        d = liq.get_liquidation_data(coin_id)
        if d:
            lines.append(
                f"{symbol} L/S ratio: {d['ls_ratio']:.2f} "
                f"(Longs {d['long_pct']:.1f}% / Shorts {d['short_pct']:.1f}%), "
                f"OI change 1h: {d['oi_change']:+.2f}%, pressure: {d['pressure']}"
                if d['oi_change'] is not None else
                f"{symbol} L/S ratio: {d['ls_ratio']:.2f}, pressure: {d['pressure']}"
            )

    return "\n".join(lines)


@st.cache_data(ttl=900, show_spinner=False)
def get_summary() -> str:
    key = _api_key()
    if not key:
        return ""

    context = _build_context()

    prompt = f"""Du bist ein präziser Crypto-Markt-Analyst. Aktuelle Marktdaten:

{context}

Antworte NUR in diesem exakten Format (kein Markdown, keine Sterne, keine Erklärungen):

VERDICT: [BULLISH / BEARISH-NEUTRAL / NEUTRAL / BEARISH] – [ein Satz Begründung]
• [Beobachtung zu Gesamtmarkt/Stimmung, max 12 Wörter]
• [Beobachtung zu BTC/ETH/SOL Stärke oder Schwäche, max 12 Wörter]
• [Liquidationsrisiko oder wichtigster Warnhinweis, max 12 Wörter]"""

    try:
        client = anthropic.Anthropic(api_key=key)
        msg = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=200,
            messages=[{"role": "user", "content": prompt}],
        )
        return msg.content[0].text.strip()
    except Exception:
        return ""
