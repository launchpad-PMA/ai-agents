"""House rooms. The talk's agent list is the shape, not our roster.

Aragamago is the cleric and the only Telegram bot. Cursor is the development
AI, in a separate room the cleric cannot open. Max stays closed while RSS3
moves to Ethereum. Legal, John Bushe, the hall of records, and the twins
room are reserved.
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
            "Administrative cleric for the church. Keeps the sacred library, "
            "tasks, calendar, and this Telegram desk. Reports back to Baba. "
            "Does not speak as Baba and does not edit the code."
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
        id="cursor",
        title="Cursor",
        role=(
            "Development AI. Builds and changes this repo. Dev credentials stay "
            "with Cursor and are not the house keys. The cleric does not open this room."
        ),
        status="development",
        credentials=(),
    ),
    Room(
        id="legal",
        title="Legal",
        role="Reserved. No legal bot is built yet, and this room has no files and no credentials.",
        status="reserved",
        credentials=(),
    ),
    Room(
        id="john-bushe",
        title="John Bushe",
        role=(
            "Reserved AI twin for AdBongo. Social videos and business would live here later. "
            "Not built. The chief does not speak as this twin."
        ),
        status="reserved",
        credentials=(),
    ),
    Room(
        id="hall-of-records",
        title="Hall of Records",
        role=(
            "Reserved library for the church. Elder knowledge would be kept here as records. "
            "Not built. A record is not a speaking twin."
        ),
        status="reserved",
        credentials=(),
    ),
    Room(
        id="twins",
        title="Twins",
        role=(
            "Reserved room for AI twins of important people, including elders for the church. "
            "Not built. Each twin stays in this room, apart from the hall of records."
        ),
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
        "The cleric does not read another room's files.",
    ]
    for room in ROOMS:
        lines.append(f"{room.title} ({room.status}): {room.role}")
    return "\n".join(lines)
