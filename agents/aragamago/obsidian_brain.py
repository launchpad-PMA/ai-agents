"""Append Telegram turns to a Markdown note in the Obsidian vault.

Default folder, next to the existing agent files:

    /home/baba2-mainoffice/Documents/Obsidian Vault/Agents/brain

Override with OBSIDIAN_BRAIN_DIR. The note is only written when that folder's
parent already exists, or when OBSIDIAN_BRAIN_DIR is set. Railway does not
have the vault, so a missing folder is skipped instead of creating a fake one.
"""

from __future__ import annotations

import os
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

DEFAULT_BRAIN_DIR = Path(
    "/home/baba2-mainoffice/Documents/Obsidian Vault/Agents/brain"
)
CHICAGO = ZoneInfo("America/Chicago")


def brain_dir() -> Path | None:
    override = os.environ.get("OBSIDIAN_BRAIN_DIR", "").strip()
    if override:
        path = Path(override).expanduser()
        path.mkdir(parents=True, exist_ok=True)
        return path
    if DEFAULT_BRAIN_DIR.parent.is_dir():
        DEFAULT_BRAIN_DIR.mkdir(parents=True, exist_ok=True)
        return DEFAULT_BRAIN_DIR
    return None


def _note_path(folder: Path, chat_id: str) -> Path:
    safe = "".join(ch for ch in str(chat_id) if ch.isalnum() or ch in "-_") or "chat"
    return folder / f"telegram-{safe}.md"


def _stamp() -> str:
    return datetime.now(CHICAGO).strftime("%Y-%m-%d %H:%M %Z")


def render_turn(role: str, content: str, when: str | None = None) -> str:
    label = "Aragamago" if role == "assistant" else role.capitalize()
    body = (content or "").strip()
    return f"### {when or _stamp()}\n\n**{label}:** {body}\n"


def save_turn(chat_id: str, role: str, content: str) -> bool:
    folder = brain_dir()
    text = (content or "").strip()
    if folder is None or not chat_id or not text:
        return False
    path = _note_path(folder, chat_id)
    if not path.exists():
        path.write_text(
            "---\n"
            "tags:\n"
            "  - aragamago\n"
            "  - telegram\n"
            f"chat_id: \"{chat_id}\"\n"
            "---\n\n"
            f"# Telegram {chat_id}\n\n",
            encoding="utf-8",
        )
    with path.open("a", encoding="utf-8") as handle:
        handle.write(render_turn(role, text) + "\n")
    return True
