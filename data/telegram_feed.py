"""WatcherGuru messages via Telegram MTProto API (telethon)."""
from __future__ import annotations

import base64
import os
import tempfile
from datetime import datetime, timezone
from pathlib import Path

import streamlit as st
from telethon.sync import TelegramClient

_CHANNEL = "WatcherGuru"
_LOCAL_SESSION = str(Path(__file__).parent.parent / "tg_session")


def _credentials() -> tuple[int, str, str | None]:
    try:
        api_id   = int(st.secrets["TG_API_ID"])
        api_hash = st.secrets["TG_API_HASH"]
    except Exception:
        api_id   = int(os.environ.get("TG_API_ID", 0))
        api_hash = os.environ.get("TG_API_HASH", "")

    session_b64 = None
    try:
        session_b64 = st.secrets.get("TG_SESSION_B64")
    except Exception:
        pass
    if not session_b64:
        session_b64 = os.environ.get("TG_SESSION_B64")

    return api_id, api_hash, session_b64


def _get_session_path(session_b64: str | None) -> str:
    """Use local file if available, else write session from env var to tmp."""
    local = Path(_LOCAL_SESSION + ".session")
    if local.exists():
        return _LOCAL_SESSION

    if session_b64:
        tmp = Path(tempfile.gettempdir()) / "tg_session.session"
        if not tmp.exists():
            # fix missing base64 padding
            padded = session_b64 + "=" * (-len(session_b64) % 4)
            tmp.write_bytes(base64.b64decode(padded))
        return str(tmp.with_suffix(""))

    return _LOCAL_SESSION


@st.cache_data(ttl=45, show_spinner=False)
def get_messages(limit: int = 20) -> list[dict]:
    api_id, api_hash, session_b64 = _credentials()
    if not api_id or not api_hash:
        return []

    session_path = _get_session_path(session_b64)

    try:
        with TelegramClient(session_path, api_id, api_hash) as client:
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
