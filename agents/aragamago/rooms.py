"""Our rooms. The talk's agent list is an example of the shape, not our roster.

Each room has its own knowledge and its own credentials. The chief of staff
can name another room. It does not read that room's files.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Room:
    id: str
    title: str
    role: str
    credentials: tuple[str, ...]


ROOMS: tuple[Room, ...] = (
    Room(
        id="aragamago",
        title="Aragamago",
        role=(
            "Chief of staff. Sets priorities, delegates, and reports to Baba. "
            "Holds the sacred library, tasks, calendar, and this Telegram conversation."
        ),
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
            "Comm agent. RSS3 node, Farcaster, and the public site. "
            "Its credentials stay on that service."
        ),
        credentials=("NEYNAR_API_KEY", "NEYNAR_SIGNER_UUID", "YOUTUBE_API_KEY"),
    ),
)

ROOM_IDS = {room.id for room in ROOMS}


def room_by_id(room_id: str) -> Room | None:
    key = (room_id or "").strip().lower()
    for room in ROOMS:
        if room.id == key:
            return room
    return None


def staff_directory() -> str:
    lines = [
        "Our rooms. Each has its own knowledge and its own credentials. "
        "A turn for one room does not read another room's files.",
    ]
    for room in ROOMS:
        lines.append(f"{room.title}: {room.role}")
    lines.append("Further rooms are added only when Baba names them.")
    return "\n".join(lines)
