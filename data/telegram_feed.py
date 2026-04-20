"""WatcherGuru messages via Telegram MTProto API (telethon)."""
from __future__ import annotations

import os
from datetime import datetime, timezone
from pathlib import Path

import streamlit as st
from telethon.sync import TelegramClient
from telethon.sessions import StringSession

_CHANNEL     = "WatcherGuru"
_LOCAL_SESSION = str(Path(__file__).parent.parent / "tg_session")


def _credentials() -> tuple[int, str, str | None]:
    try:
        api_id   = int(st.secrets["TG_API_ID"])
        api_hash = st.secrets["TG_API_HASH"]
    except Exception:
        api_id   = int(os.environ.get("TG_API_ID", 0))
        api_hash = os.environ.get("TG_API_HASH", "")

    # StringSession (short string, preferred for cloud deploy)
    session_str = None
    try:
        session_str = st.secrets.get("TG_SESSION_STRING")
    except Exception:
        pass
    if not session_str:
        session_str = os.environ.get("TG_SESSION_STRING")

    return api_id, api_hash, session_str


@st.cache_data(ttl=45, show_spinner=False)
def get_messages(limit: int = 20) -> list[dict]:
    api_id, api_hash, session_str = _credentials()
    if not api_id or not api_hash:
        return []

    # Use StringSession if available (Railway), else local file (dev)
    local = Path(_LOCAL_SESSION + ".session")
    if session_str:
        session = StringSession(session_str)
    elif local.exists():
        session = _LOCAL_SESSION
    else:
        return []

    try:
        with TelegramClient(session, api_id, api_hash) as client:
            raw = client.get_messages(_CHANNEL, limit=limit)

        items = []
        for m in raw:
            text = (m.text or m.message or "").strip().replace("**", "").replace("__", "")
            if not text:
                continue
            dt   = m.date.replace(tzinfo=timezone.utc) if m.date.tzinfo is None else m.date
            mins = int((datetime.now(timezone.utc) - dt).total_seconds() / 60)
            if mins < 60:
                age = f"{mins}m"
            elif mins < 1440:
                age = f"{mins // 60}h"
            else:
                age = f"{mins // 1440}d"
            link = f"https://t.me/{_CHANNEL}/{m.id}"
            items.append({"text": text, "age": age, "link": link})

        return items
    except Exception:
        return []
