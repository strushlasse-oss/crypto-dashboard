"""Sidebar: core coins, coin search, global settings."""
from __future__ import annotations

from datetime import timezone

import streamlit as st

from data import coingecko as cg
from data import fear_greed as fg
from data import global_metrics as gm


def render() -> dict:
    """Render sidebar and return user-selected state."""
    with st.sidebar:
        st.markdown("### Coins")
        st.caption("Solana, Bitcoin, Ethereum sind immer aktiv.")

        st.markdown("#### Weitere Coins hinzufügen")
        query = st.text_input("Suche (z. B. 'avalanche')", key="coin_query")
        extra: list[dict] = st.session_state.setdefault("extra_coins", [])

        if query:
            results = cg.search_coins(query)
            if results:
                options = {
                    f"{c['name']} ({c['symbol'].upper()})": c
                    for c in results
                    if c.get("id")
                }
                choice = st.selectbox("Treffer", [""] + list(options.keys()),
                                      key="coin_choice")
                if choice and st.button("Hinzufügen", key="add_coin"):
                    sel = options[choice]
                    if not any(e["id"] == sel["id"] for e in extra):
                        extra.append({
                            "id": sel["id"],
                            "symbol": sel.get("symbol", ""),
                            "name": sel.get("name", sel["id"]),
                        })
                        st.session_state["coin_query"] = ""
                        st.rerun()
            else:
                st.caption("Keine Treffer.")

        if extra:
            st.markdown("#### Hinzugefügt")
            for c in list(extra):
                row = st.columns([4, 1])
                row[0].write(f"{c['name']} ({c['symbol'].upper()})")
                if row[1].button("×", key=f"rm_{c['id']}"):
                    extra.remove(c)
                    st.rerun()

        st.divider()
        st.markdown("### Einstellungen")
        days = st.select_slider(
            "Indikator-Zeitraum (Tage)",
            options=[14, 30, 60, 90, 180, 365],
            value=90,
        )
        auto_refresh = st.toggle("Auto-Refresh (120 s)", value=False)

        try:
            fng_list = fg.get_fear_greed(limit=1)
            fng = fng_list[0] if fng_list else None
        except Exception:  # noqa: BLE001
            fng = None

        st.divider()

        # Economic Calendar
        with st.expander("📅 Economic Calendar", expanded=False):
            events = gm.get_calendar(impact_filter="High")
            if not events:
                st.caption("Keine Daten verfügbar.")
            else:
                from datetime import datetime
                now = datetime.now(timezone.utc)
                shown = 0
                for e in events:
                    diff = e["diff_sec"]
                    if diff < -3600:  # skip events older than 1h
                        continue
                    dt_local = e["date"]
                    time_str = dt_local.strftime("%a %d. %b %H:%M UTC")
                    if diff > 0:
                        h, m = int(diff // 3600), int((diff % 3600) // 60)
                        countdown = f"in {h}h {m}m" if h else f"in {m}m"
                        badge_color = "#f7a832" if diff < 7200 else "#888"
                    else:
                        countdown = "läuft gerade"
                        badge_color = "#ff4455"

                    forecast = e.get("forecast") or "–"
                    previous = e.get("previous") or "–"
                    actual   = e.get("actual")  or ""

                    st.markdown(
                        f"<div style='padding:6px 0;border-bottom:1px solid rgba(255,255,255,0.06)'>"
                        f"<div style='font-size:12px;font-weight:700;color:#e0e0e0'>{e['title']}"
                        f" <span style='font-size:10px;color:#888'>({e['country']})</span></div>"
                        f"<div style='font-size:10px;color:#888;margin-top:2px'>{time_str}"
                        f" · <span style='color:{badge_color}'>{countdown}</span></div>"
                        f"<div style='font-size:10px;color:#aaa;margin-top:2px'>"
                        f"Prognose: {forecast} · Vorher: {previous}"
                        + (f" · <b style='color:#00d084'>Aktuell: {actual}</b>" if actual else "")
                        + "</div></div>",
                        unsafe_allow_html=True,
                    )
                    shown += 1
                    if shown >= 10:
                        break
                if shown == 0:
                    st.caption("Keine anstehenden Ereignisse.")

        st.divider()
        if st.button("Cache leeren", width="stretch"):
            st.cache_data.clear()
            st.rerun()

    return {"extra": extra, "days": days, "auto_refresh": auto_refresh, "fng": fng}
