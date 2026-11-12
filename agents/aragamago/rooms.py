"""House rooms. The talk's agent list is the shape, not our roster.

Aragamago is the cleric and the only Telegram bot. Cursor is the development
AI, in a separate room the cleric cannot open. Max stays closed while RSS3
moves to Ethereum. John Bushe is the main bot, still unbuilt.
Legal, the hall of records, and the twins room are reserved.
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
            "Publisher. On hold while RSS3 moves to Ethereum. "
            "The only content post he can make today is a Farcaster cast through Neynar. "
            "YouTube is a live check that he announces on Farcaster. He does not upload videos "
            "or post to other social networks. Credentials stay on his service."
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
            "Main bot. Baba's twin for AdBongo: voice, social video, and business. "
            "His brain is mapped inside this room by one archaeologist with five jobs: "
            "researcher, archivist, action, content, and review. The researcher scrapes. "
            "Sources, when built: Gmail, Google Drive, exported ChatGPT logs, Apple notes, and Obsidian. "
            "Not built. The cleric does not speak as him or read this room."
        ),
        status="main",
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

# Jobs inside the John Bushe room. They are not separate house rooms.
ARCHAEOLOGIST: tuple[tuple[str, str], ...] = (
    (
        "researcher",
        "Scrapes Gmail, Google Drive, exported ChatGPT logs, Apple notes, Obsidian, and the NAS "
        "onto the knowledge shelf. Originals stay where they are. This is not Hermes and not Max.",
    ),
    (
        "archivist",
        "Cleans, classifies, and deduplicates into five collections. Originals are kept. Not one vault.",
    ),
    ("action", "Extracts tasks, drops what is no longer relevant, and prepares a daily list."),
    (
        "content",
        "Hermes content studio: discover, research, draft, and verify. "
        "Drafts stay here until Baba approves. Max publishes. There is no second publisher.",
    ),
    (
        "review",
        "Flags confidential information, unsupported claims, and duplicates before anything leaves the room. "
        "Gauges a draft as marketing, a membership perk, or a sale. The gauge recommends. "
        "Max decides and is the only publisher.",
    ),
)

# The archivist's shelves inside the John Bushe room. Not house rooms, and not one vault.
COLLECTIONS: tuple[tuple[str, str], ...] = (
    ("action", "Open tasks, promises, deadlines, follow-ups, and project milestones."),
    ("ideas", "Business concepts, inventions, research, spiritual teachings, and strategic insights."),
    ("content", "Article drafts, video scripts, podcast topics, and social material."),
    ("projects", "AdBongo, Temple of Roots, LexClinic, the AI infrastructure, and other projects."),
    (
        "knowledge",
        "Source conversations, emails, documents, research, and reference material. "
        "Each record keeps its original source, date, project, and privacy. "
        "This shelf is not the hall of records.",
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
