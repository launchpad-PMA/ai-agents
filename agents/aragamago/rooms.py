"""House rooms. The talk's agent list is the shape, not our roster.

Aragamago is the chief of staff and the only active bot. Max stays closed
while RSS3 moves to Ethereum. Legal is a reserved room with no bot yet.
Each room has its own files and its own credentials. The chief can name
another room. It does not read that room's files.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Room:
    id: str
    title: str
    role: str
    status: str
    credentials: tuple[str, ...]


ROOMS: tuple[Room, ...] = (
    Room(
        id="aragamago",
        title="Aragamago",
        role=(
            "Chief of staff, the Jarvis for Baba. Sets priorities, delegates, "
            "and reports back. Holds the sacred library, tasks, calendar, and "
            "this Telegram conversation."
        ),
        status="active",
        credentials=(
            "TELEGRAM_BOT_TOKEN",
            "OPENROUTER_API_KEY",
            "GEMINI_API_KEY",
            "ELEVENLABS_API_KEY",
            "PINECONE_API_KEY",
        ),
    ),
    Room(
        id="maxayauwi",
        title="Maxayauwi",
        role=(
            "Comm agent for the RSS3 node, Farcaster, and the public site. "
            "On hold while RSS3 moves to Ethereum. Its credentials stay on that service."
        ),
        status="hold",
        credentials=("NEYNAR_API_KEY", "NEYNAR_SIGNER_UUID", "YOUTUBE_API_KEY"),
    ),
    Room(
        id="legal",
        title="Legal",
        role="Reserved. No legal bot is built yet, and this room has no files and no credentials.",
        status="reserved",
        credentials=(),
    ),
)

ROOM_IDS = {room.id for room in ROOMS}


def room_by_id(room_id: str) -> Room | None:
    key = (room_id or "").strip().lower()
    for room in ROOMS:
        if room.id == key:
            return room
    return None


def active_room() -> Room:
    for room in ROOMS:
        if room.status == "active":
            return room
    return ROOMS[0]


def staff_directory() -> str:
    lines = [
        "Private rooms. Each has its own knowledge and its own credentials. "
        "The chief of staff does not read another room's files.",
    ]
    for room in ROOMS:
        lines.append(f"{room.title} ({room.status}): {room.role}")
    return "\n".join(lines)
