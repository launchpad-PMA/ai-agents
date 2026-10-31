"""Short transcript for one Telegram chat.

This is the memory that keeps the previous message. It lives in the bot
process. Supabase is not used. Pinecone is a separate long-term index and
does not receive these turns.
"""

from __future__ import annotations

from collections import deque

_MAX_TURNS = 12
_transcripts: dict[str, deque[tuple[str, str]]] = {}


def remember(chat_id: str, role: str, content: str) -> None:
    text = (content or "").strip()
    if not chat_id or not text:
        return
    turns = _transcripts.setdefault(str(chat_id), deque(maxlen=_MAX_TURNS))
    turns.append((role, text[:2000]))


def recent(chat_id: str, limit: int = 6) -> str:
    turns = list(_transcripts.get(str(chat_id), ()))[-limit:]
    return "\n".join(f"{role.capitalize()}: {text}" for role, text in turns)


def clear(chat_id: str | None = None) -> None:
    if chat_id is None:
        _transcripts.clear()
        return
    _transcripts.pop(str(chat_id), None)
