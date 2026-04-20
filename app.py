"""Streamlit entry point for the local crypto analysis dashboard."""
from __future__ import annotations

import time
from datetime import datetime

import streamlit as st
from dotenv import load_dotenv

from data import coingecko as cg
from data import news as news_mod
from ui import coin_card, landing, sidebar, styles

load_dotenv()

st.set_page_config(
    page_title="Crypto Dashboard",
    page_icon="₿",
    layout="wide",
    initial_sidebar_state="expanded",
)

styles.inject()

_now = datetime.now()
_date_str = _now.strftime("%A, %d. %B %Y · %H:%M")
_de_days = {
    "Monday": "Montag", "Tuesday": "Dienstag", "Wednesday": "Mittwoch",
    "Thursday": "Donnerstag", "Friday": "Freitag", "Saturday": "Samstag",
    "Sunday": "Sonntag",
}
_de_months = {
    "January": "Januar", "February": "Februar", "March": "März", "April": "April",
    "May": "Mai", "June": "Juni", "July": "Juli", "August": "August",
    "September": "September", "October": "Oktober", "November": "November",
    "December": "Dezember",
}
for _en, _de in {**_de_days, **_de_months}.items():
    _date_str = _date_str.replace(_en, _de)

st.markdown(
    f"""
    <div class='hero'>
      <div class='hero-greeting'>Willkommen zurück, Lasse.</div>
      <div class='hero-sub'>
        <span class='hero-sub-icon'>⬥</span>
        Dein persönliches Crypto-Dashboard · powered by AI &nbsp;·&nbsp; {_date_str}
      </div>
    </div>
    """,
    unsafe_allow_html=True,
)

state = sidebar.render()

core = cg.CORE_COINS
extras = state["extra"]
all_coins = core + extras
ids = [c["id"] for c in all_coins]

try:
    markets = cg.get_markets(ids)
except Exception as e:  # noqa: BLE001
    st.error(f"CoinGecko nicht erreichbar: {e}")
    st.stop()

markets_by_id = {m["id"]: m for m in markets}

selected_id = st.session_state.get("selected_coin")
fng_value = int(state["fng"]["value"]) if state["fng"] and state["fng"].get("value") else None

if selected_id is None:
    landing.render(core, markets_by_id, fng_value)
else:
    nav_l, nav_r = st.columns([1, 6])
    with nav_l:
        if st.button("← Übersicht", width="stretch"):
            st.session_state.pop("selected_coin", None)
            st.rerun()
    with nav_r:
        core_labels = [c["name"] for c in core]
        current_label = next(
            (c["name"] for c in core if c["id"] == selected_id), core_labels[0]
        )
        chosen = st.segmented_control(
            "Coin",
            options=core_labels,
            default=current_label,
            label_visibility="collapsed",
            key="core_coin_switch",
        )
        chosen_coin = next((c for c in core if c["name"] == chosen), core[0])
        if chosen_coin["id"] != selected_id:
            st.session_state["selected_coin"] = chosen_coin["id"]
            st.rerun()

    coin = next((c for c in core if c["id"] == selected_id), None)
    if coin is None:
        st.warning("Coin nicht gefunden.")
    else:
        m = markets_by_id.get(coin["id"])
        if not m:
            st.warning(f"Keine Marktdaten für {coin['name']}.")
        else:
            coin_card.render(coin, m, fear_greed=state["fng"], days=state["days"])

if extras:
    st.subheader("Weitere Coins")
    for coin in extras:
        m = markets_by_id.get(coin["id"])
        if not m:
            st.warning(f"Keine Marktdaten für {coin['name']}.")
            continue
        with st.container(border=True):
            coin_card.render(coin, m, fear_greed=state["fng"], days=state["days"])

if news_mod.is_enabled():
    st.subheader("News (CryptoPanic)")
    try:
        items = news_mod.get_news(
            currencies=[c["symbol"].upper() for c in all_coins],
            limit=15,
        )
        if not items:
            st.caption("Keine News geladen.")
        else:
            for it in items:
                st.markdown(
                    f"- [{it['title']}]({it['url']}) — "
                    f"_{it.get('source') or 'Quelle'}_ · "
                    f"{', '.join(it.get('currencies') or []) or '—'}"
                )
    except Exception as e:  # noqa: BLE001
        st.caption(f"News-Fehler: {e}")

if state["auto_refresh"]:
    time.sleep(120)
    st.rerun()
