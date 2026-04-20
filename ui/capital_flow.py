"""Capital Flow widget: horizontal momentum bars sorted by 24h performance."""
from __future__ import annotations

import streamlit as st

from ui.styles import GREEN, RED, TEXT_DIM, TEXT_MUTED


def _bar_html(symbol: str, pct: float, max_abs: float) -> str:
    is_pos = pct >= 0
    color = GREEN if is_pos else RED
    fill_pct = min(100, abs(pct) / max(max_abs, 0.01) * 100)
    val_str = f"{pct:+.2f}%"
    return (
        f"<div class='flow-row'>"
        f"<div class='flow-label'>{symbol}</div>"
        f"<div class='flow-bar-bg'>"
        f"<div class='flow-bar-fill' style='width:{fill_pct:.1f}%;background:{color}'></div>"
        f"</div>"
        f"<div class='flow-value' style='color:{color}'>{val_str}</div>"
        f"</div>"
    )


def render(markets: list[dict]) -> None:
    """Render the Capital Flow section from a list of CoinGecko market dicts."""
    if not markets:
        return

    rows = []
    for m in markets:
        symbol = (m.get("symbol") or m.get("id", "?")).upper()
        pct = m.get("price_change_percentage_24h_in_currency")
        if pct is None:
            pct = m.get("price_change_percentage_24h") or 0.0
        rows.append((symbol, float(pct)))

    rows.sort(key=lambda x: x[1], reverse=True)
    max_abs = max(abs(p) for _, p in rows) if rows else 1.0

    bars_html = "".join(_bar_html(sym, pct, max_abs) for sym, pct in rows)

    st.markdown(
        f"<div class='flow-header'>"
        f"<span style='font-size:0.72rem;text-transform:uppercase;letter-spacing:0.1em;"
        f"color:{TEXT_MUTED};font-weight:600'>Capital Flow · 24h</span>"
        f"<span class='live-badge'><span class='live-dot'></span>Live</span>"
        f"</div>"
        f"{bars_html}",
        unsafe_allow_html=True,
    )
