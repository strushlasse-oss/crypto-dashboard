"""Short AI snapshot (2-3 sentences) for the coin detail header.

Cached for 30 minutes per (coin_id, price-bucket) so we don't hammer the
API on every rerun. Falls back to a deterministic text built from the
Edge Factor components when ANTHROPIC_API_KEY is missing or the call fails.
"""
from __future__ import annotations

import os

import streamlit as st
from anthropic import Anthropic

from analysis.edge_factor import EdgeResult

DEFAULT_MODEL = "claude-sonnet-4-6"
SYSTEM_PROMPT = (
    "Du bist ein erfahrener Krypto-Analyst. Liefere eine sehr knappe "
    "Live-Einschätzung in 2-3 deutschen Sätzen. Beziehe dich auf die "
    "übergebenen Indikatoren UND den Makro-Kontext (Fear & Greed, Trend). "
    "Keine Preisziele, keine Anlageempfehlung, keine Floskeln."
)


def _client() -> Anthropic | None:
    key = os.getenv("ANTHROPIC_API_KEY")
    if not key:
        return None
    return Anthropic(api_key=key)


def _bucket_price(price: float | None) -> int:
    """Round price to a coarse bucket so the cache key is stable for ~30 min
    even when the live price wiggles by fractions of a percent."""
    if not price or price <= 0:
        return 0
    if price >= 1000:
        return int(round(price / 50) * 50)
    if price >= 10:
        return int(round(price / 0.5) * 1)
    return int(round(price * 100))


def _fallback(name: str, edge: EdgeResult, fng_value: int | None) -> str:
    parts = [f"{name}: {edge.headline} (Edge {edge.score}/100)."]
    pos = [c.note for c in edge.components if c.points >= c.max_points * 0.6][:2]
    neg = [c.note for c in edge.components if c.points <= c.max_points * 0.3][:2]
    if pos:
        parts.append("Stützend: " + "; ".join(pos) + ".")
    if neg:
        parts.append("Belastend: " + "; ".join(neg) + ".")
    if fng_value is not None and not pos:
        parts.append(f"Marktstimmung Fear & Greed bei {fng_value}.")
    return " ".join(parts)


@st.cache_data(ttl=1800, show_spinner=False)
def _generate(coin_id: str, name: str, price_bucket: int, edge_score_v: int,
              edge_headline: str, edge_comment: str, fng_value: int | None,
              trend: str) -> str:
    client = _client()
    if client is None:
        return ""  # signal: caller must use fallback
    payload = (
        f"Coin: {name} ({coin_id})\n"
        f"Edge Factor Score: {edge_score_v}/100 ({edge_headline})\n"
        f"Edge Comment: {edge_comment}\n"
        f"Fear & Greed: {fng_value if fng_value is not None else 'n/a'}\n"
        f"Trend (SMA-Lage): {trend}\n"
    )
    try:
        msg = client.messages.create(
            model=os.getenv("CLAUDE_MODEL", DEFAULT_MODEL),
            max_tokens=220,
            system=SYSTEM_PROMPT,
            messages=[{"role": "user", "content": payload}],
        )
        text = "\n".join(
            b.text for b in msg.content if getattr(b, "type", None) == "text"
        ).strip()
        return text
    except Exception:  # noqa: BLE001
        return ""


def snapshot(coin_id: str, name: str, price: float | None,
             edge: EdgeResult, fng_value: int | None,
             trend: str) -> tuple[str, bool]:
    """Return (text, is_ai). If AI is unavailable, returns deterministic fallback."""
    bucket = _bucket_price(price)
    text = _generate(
        coin_id=coin_id, name=name, price_bucket=bucket,
        edge_score_v=edge.score, edge_headline=edge.headline,
        edge_comment=edge.comment, fng_value=fng_value, trend=trend,
    )
    if text:
        return text, True
    return _fallback(name, edge, fng_value), False
