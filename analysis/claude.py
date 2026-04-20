"""Claude-powered coin analysis.

Model defaults to claude-sonnet-4-6 (fast + cheap); override via CLAUDE_MODEL env.
"""
from __future__ import annotations

import os
from typing import Any

from anthropic import Anthropic

DEFAULT_MODEL = "claude-sonnet-4-6"
MAX_TOKENS = 1200

SYSTEM_PROMPT = (
    "Du bist ein erfahrener Krypto-Analyst. Du bekommst aktuelle Marktdaten und "
    "technische Indikatoren zu einem Coin. Liefere eine knappe, strukturierte "
    "Analyse auf Deutsch mit folgenden Abschnitten:\n"
    "1. **Kurzfazit** (1–2 Sätze)\n"
    "2. **Technische Lage** (RSI, MACD, SMA, Bollinger – was sagen sie zusammen?)\n"
    "3. **Momentum & Volumen**\n"
    "4. **Mögliche Szenarien** (bullish / bearish, jeweils 1–2 Zeilen)\n"
    "5. **Risiken / Unsicherheiten**\n\n"
    "Wichtig: keine Finanzberatung, keine konkreten Preisziele garantieren, "
    "Unsicherheiten klar benennen."
)


class ClaudeUnavailable(RuntimeError):
    """Raised when ANTHROPIC_API_KEY is missing."""


def _client() -> Anthropic:
    key = os.getenv("ANTHROPIC_API_KEY")
    if not key:
        raise ClaudeUnavailable(
            "ANTHROPIC_API_KEY ist nicht gesetzt. Trage den Key in die .env-Datei ein."
        )
    return Anthropic(api_key=key)


def _format_payload(name: str, symbol: str, market: dict, snapshot: dict,
                    trend: str, fear_greed: dict | None) -> str:
    def fmt(v: Any, digits: int = 2) -> str:
        if v is None:
            return "n/a"
        if isinstance(v, (int, float)):
            return f"{v:,.{digits}f}"
        return str(v)

    lines = [
        f"Coin: {name} ({symbol.upper()})",
        f"Aktueller Kurs: {fmt(market.get('current_price'), 4)} USD",
        f"Marktkapitalisierung: {fmt(market.get('market_cap'), 0)} USD",
        f"24h-Volumen: {fmt(market.get('total_volume'), 0)} USD",
        f"Änderung 1h: {fmt(market.get('price_change_percentage_1h_in_currency'))}%",
        f"Änderung 24h: {fmt(market.get('price_change_percentage_24h_in_currency'))}%",
        f"Änderung 7d: {fmt(market.get('price_change_percentage_7d_in_currency'))}%",
        f"Änderung 30d: {fmt(market.get('price_change_percentage_30d_in_currency'))}%",
        f"52w-Hoch: {fmt(market.get('ath'), 4)} USD  |  52w-Tief: {fmt(market.get('atl'), 4)} USD",
        "",
        f"Trend-Label (aus SMAs): {trend}",
        "Indikatoren (letzter Wert):",
        f"  RSI(14): {fmt(snapshot.get('rsi_14'))}",
        f"  MACD: {fmt(snapshot.get('macd'), 4)}  "
        f"Signal: {fmt(snapshot.get('macd_signal'), 4)}  "
        f"Hist: {fmt(snapshot.get('macd_hist'), 4)}",
        f"  SMA50: {fmt(snapshot.get('sma_50'), 4)}  "
        f"SMA200: {fmt(snapshot.get('sma_200'), 4)}",
        f"  Bollinger: lower {fmt(snapshot.get('bb_lower'), 4)} / "
        f"mid {fmt(snapshot.get('bb_mid'), 4)} / "
        f"upper {fmt(snapshot.get('bb_upper'), 4)}",
    ]
    if fear_greed:
        lines.append("")
        lines.append(
            f"Fear & Greed Index: {fear_greed.get('value')} "
            f"({fear_greed.get('value_classification')})"
        )
    return "\n".join(lines)


def analyze_coin(name: str, symbol: str, market: dict, snapshot: dict,
                 trend: str, fear_greed: dict | None = None,
                 model: str | None = None) -> str:
    client = _client()
    payload = _format_payload(name, symbol, market, snapshot, trend, fear_greed)
    msg = client.messages.create(
        model=model or os.getenv("CLAUDE_MODEL", DEFAULT_MODEL),
        max_tokens=MAX_TOKENS,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": payload}],
    )
    parts = [block.text for block in msg.content if getattr(block, "type", None) == "text"]
    return "\n".join(parts).strip()
