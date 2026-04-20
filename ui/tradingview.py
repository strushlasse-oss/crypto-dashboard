"""TradingView Advanced Chart widget embed."""
from __future__ import annotations

import json

import streamlit as st


def render(tv_symbol: str, height: int = 520, container_id: str | None = None) -> None:
    """Embed the TradingView advanced-chart widget in dark mode.

    tv_symbol: e.g. "BINANCE:BTCUSDT" or "COINBASE:SOLUSD".
    """
    cid = container_id or f"tv_{tv_symbol.replace(':', '_').lower()}"
    config = {
        "autosize": True,
        "symbol": tv_symbol,
        "interval": "240",
        "timezone": "Etc/UTC",
        "theme": "dark",
        "style": "1",
        "locale": "de_DE",
        "enable_publishing": False,
        "withdateranges": True,
        "hide_side_toolbar": False,
        "allow_symbol_change": True,
        "details": True,
        "hotlist": False,
        "calendar": False,
        "studies": [],
        "container_id": cid,
    }
    html = f"""
    <div class="tradingview-widget-container" style="height:{height}px;width:100%">
      <div id="{cid}" style="height:{height}px;width:100%"></div>
      <script type="text/javascript" src="https://s3.tradingview.com/tv.js"></script>
      <script type="text/javascript">
        new TradingView.widget({json.dumps(config)});
      </script>
    </div>
    """
    st.iframe(html, height=height + 20)
