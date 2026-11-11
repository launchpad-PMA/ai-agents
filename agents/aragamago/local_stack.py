"""Local AI stack for the home machine.

The machine runs the models. Ollama serves them. Knowledge is plain text Baba controls.

Aragamago is the chief of staff. Maxayauwi is a separate room. A search for one
room does not open the other room's files. The talk's agent list is not our roster.

Railway stays on the cloud providers. Ollama is used only when OLLAMA_BASE_URL is set.
"""

from __future__ import annotations

import json
import os
import re
import urllib.error
import urllib.request
from datetime import datetime
from pathlib import Path

from agents.aragamago.rooms import ROOM_IDS, staff_directory

GENERAL_MODEL = "qwen3.6:27b"
VISION_MODEL = "qwen3.8:27b"
EMBED_MODEL = "nomic-embed-text"
TEMPERATURE = 0.3
NUM_CTX = 64000

_TEXT_SUFFIXES = {".md", ".txt", ".markdown"}
_STOP = {"the", "and", "for", "you", "your", "that", "this", "with", "from", "are", "was"}


def ollama_base_url() -> str:
    return os.environ.get("OLLAMA_BASE_URL", "").strip().rstrip("/")


def general_model() -> str:
    return os.environ.get("OLLAMA_MODEL", "").strip() or GENERAL_MODEL


def vision_model() -> str:
    return os.environ.get("OLLAMA_VISION_MODEL", "").strip() or VISION_MODEL


def embed_model() -> str:
    return os.environ.get("OLLAMA_EMBED_MODEL", "").strip() or EMBED_MODEL


def archive_root() -> Path | None:
    raw = os.environ.get("ARAGAMAGO_ARCHIVE", "").strip()
    if not raw:
        return None
    return Path(raw).expanduser()


def skills_dir() -> Path:
    override = os.environ.get("ARAGAMAGO_SKILLS", "").strip()
    if override:
        return Path(override).expanduser()
    return Path(__file__).resolve().parent / "skills"


def stack_status() -> dict[str, object]:
    return {
        "ollama": bool(ollama_base_url()),
        "model": general_model(),
        "vision_model": vision_model(),
        "embed_model": embed_model(),
        "archive": archive_root() is not None,
        "room": _active_room_id(),
    }


def ollama_chat(
    system: str,
    user: str,
    *,
    images: list[str] | None = None,
    model: str | None = None,
    base_url: str | None = None,
    timeout: float = 180,
) -> str | None:
    """Talk to a local Ollama server. Returns None when no server is configured."""
    base = ollama_base_url() if base_url is None else base_url.strip().rstrip("/")
    if not base:
        return None
    chosen = model or (vision_model() if images else general_model())
    user_message: dict[str, object] = {"role": "user", "content": user or ""}
    if images:
        user_message["images"] = images
    messages: list[dict[str, object]] = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append(user_message)
    payload = {
        "model": chosen,
        "messages": messages,
        "stream": False,
        "options": {"temperature": TEMPERATURE, "num_ctx": NUM_CTX},
    }
    data = _post_json(f"{base}/api/chat", payload, timeout)
    message = data.get("message") if isinstance(data, dict) else None
    content = ""
    if isinstance(message, dict):
        content = str(message.get("content") or "").strip()
    return content or None


def embed_text(text: str, *, base_url: str | None = None, timeout: float = 30) -> list[float] | None:
    base = ollama_base_url() if base_url is None else base_url.strip().rstrip("/")
    if not base or not text.strip():
        return None
    data = _post_json(
        f"{base}/api/embed",
        {"model": embed_model(), "input": text},
        timeout,
    )
    vectors = data.get("embeddings") if isinstance(data, dict) else None
    if not vectors:
        return None
    first = vectors[0]
    if not isinstance(first, list):
        return None
    return [float(value) for value in first]


def write_archive_note(
    text: str,
    *,
    source: str = "telegram",
    root: Path | None = None,
    now: datetime | None = None,
) -> bool:
    """Save one plain-text note into the local archive. No-op without a root."""
    note = (text or "").strip()
    folder = root if root is not None else archive_root()
    if folder is None or not note:
        return False
    base = _knowledge_dir(Path(folder), None)
    if base is None:
        return False
    inbox = base / "inbox"
    inbox.mkdir(parents=True, exist_ok=True)
    stamp = (now or datetime.now()).strftime("%Y%m%d%H%M%S")
    slug = re.sub(r"[^a-z0-9]+", "-", note.lower()).strip("-")[:40] or "note"
    path = inbox / f"{stamp}-{slug}.md"
    if path.exists():
        path = inbox / f"{stamp}-{slug}-2.md"
    safe_source = re.sub(r"[^a-z0-9_-]+", "", source.lower()) or "note"
    path.write_text(f"---\nsource: {safe_source}\n---\n\n{note}\n", encoding="utf-8")
    return True


def search_archive(query: str, *, root: Path | None = None, room: str | None = None, limit: int = 3) -> str:
    folder = root if root is not None else archive_root()
    if folder is None or not Path(folder).is_dir():
        return ""
    base = _knowledge_dir(Path(folder), room)
    if base is None:
        return ""
    tokens = [
        token
        for token in re.findall(r"[a-z0-9]{3,}", (query or "").lower())
        if token not in _STOP
    ]
    if not tokens:
        return ""
    scored: list[tuple[int, str, str]] = []
    for path in sorted(base.rglob("*")):
        if not path.is_file() or path.suffix.lower() not in _TEXT_SUFFIXES:
            continue
        if path.name.startswith("."):
            continue
        if not _inside(base, path):
            continue
        try:
            if path.stat().st_size > 1_000_000:
                continue
            text = path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        lowered = text.lower()
        score = sum(lowered.count(token) for token in tokens)
        if score:
            scored.append((score, path.name, _excerpt(text, tokens)))
    scored.sort(key=lambda item: (-item[0], item[1]))
    lines = [f"[{name}]: {excerpt}" for _, name, excerpt in scored[:limit]]
    return "\n\n".join(lines)


def relevant_skills(message: str, *, folder: Path | None = None) -> str:
    directory = folder if folder is not None else skills_dir()
    if not directory.is_dir() or not (message or "").strip():
        return ""
    chosen: list[str] = []
    for path in sorted(directory.glob("*.md")):
        try:
            raw = path.read_text(encoding="utf-8")
        except OSError:
            continue
        triggers = _skill_triggers(raw)
        if any(re.search(rf"\b{re.escape(trigger)}\b", message, re.IGNORECASE) for trigger in triggers):
            body = "\n".join(
                line for line in raw.splitlines() if not line.lower().startswith("triggers:")
            ).strip()
            if body:
                chosen.append(body)
    return "\n\n".join(chosen)


def local_context(message: str) -> str:
    """Skills plus this room's archive. Other rooms' files stay out."""
    parts: list[str] = []
    if re.search(r"\b(agents?|maxayauwi|delegate|rooms?)\b", message or "", re.IGNORECASE):
        parts.append(f"--- ROOMS ---\n{staff_directory()}\n--- END ROOMS ---")
    skills = relevant_skills(message)
    if skills:
        parts.append(f"--- SKILLS ---\n{skills}\n--- END SKILLS ---")
    archive = search_archive(message)
    if archive:
        parts.append(f"--- LOCAL ARCHIVE ---\n{archive}\n--- END LOCAL ARCHIVE ---")
    return "\n\n".join(parts)


def _active_room_id() -> str:
    chosen = os.environ.get("ARAGAMAGO_ROOM", "").strip().lower() or "aragamago"
    if chosen not in ROOM_IDS:
        return "aragamago"
    return chosen


def _knowledge_dir(folder: Path, room: str | None) -> Path | None:
    """Flat archive, or one room folder. Never a sibling room."""
    if not folder.is_dir():
        return None
    present = [name for name in sorted(ROOM_IDS) if (folder / name).is_dir()]
    if not present:
        return folder
    chosen = (room or _active_room_id()).strip().lower()
    if chosen not in ROOM_IDS:
        return None
    target = folder / chosen
    if not target.is_dir():
        return None
    return target


def _inside(root: Path, path: Path) -> bool:
    try:
        path.resolve().relative_to(root.resolve())
    except (OSError, ValueError):
        return False
    return True


def _skill_triggers(raw: str) -> list[str]:
    for line in raw.splitlines():
        if line.lower().startswith("triggers:"):
            return [part.strip().lower() for part in line.split(":", 1)[1].split(",") if part.strip()]
    return []


def _excerpt(text: str, tokens: list[str], window: int = 420) -> str:
    lowered = text.lower()
    at = min((lowered.find(token) for token in tokens if token in lowered), default=0)
    if at < 0:
        at = 0
    start = max(0, at - 80)
    snippet = " ".join(text[start : start + window].split())
    return snippet


def _post_json(url: str, payload: dict, timeout: float) -> dict:
    body = json.dumps(payload).encode("utf-8")
    request = urllib.request.Request(
        url,
        data=body,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            raw = response.read().decode("utf-8")
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")[:300]
        raise RuntimeError(f"Ollama {exc.code}: {detail}") from exc
    data = json.loads(raw or "{}")
    if not isinstance(data, dict):
        raise RuntimeError("Ollama returned a non-object response")
    return data
