"""Answer task, calendar, and voice questions from the tools already on the bot.

Plain chat was sending those questions to the model, which drafted a new
Cursor project instead of calling Google or ElevenLabs.
"""

from __future__ import annotations


def _flat(text: str) -> str:
    return " ".join((text or "").lower().split())


def intents_for(user_msg: str) -> set[str]:
    text = _flat(user_msg)
    hits: set[str] = set()
    if any(
        phrase in text
        for phrase in (
            "google task",
            "my tasks",
            "task list",
            "what are my tasks",
            "show my tasks",
            "show tasks",
            "list tasks",
            "list my tasks",
        )
    ):
        hits.add("tasks")
    if any(
        phrase in text
        for phrase in (
            "calendar",
            "my schedule",
            "upcoming events",
            "what's on today",
            "whats on today",
        )
    ):
        hits.add("calendar")
    if any(
        phrase in text
        for phrase in (
            "google access",
            "have google",
            "google api",
            "connect to google",
            "elevenlabs",
            "eleven labs",
            "voice talk",
            "your voice",
            "speak",
        )
    ):
        hits.add("status")
    if "task" in text and "calendar" in text:
        hits.update({"tasks", "calendar", "status"})
    return hits


def _task_lines(tasks: list, limit: int = 5) -> str:
    if not tasks:
        return "No open Google Tasks."
    lines = [f"• {task.get('title') or 'Untitled'}" for task in tasks[:limit]]
    extra = len(tasks) - limit
    if extra > 0:
        lines.append(f"• and {extra} more")
    return "\n".join(lines)


def _event_lines(events: list, limit: int = 5) -> str:
    if not events:
        return "No upcoming calendar events."
    lines = []
    for event in events[:limit]:
        start = (event.get("start") or {}).get("dateTime") or (event.get("start") or {}).get("date") or "unscheduled"
        lines.append(f"• {event.get('summary') or 'Untitled'} — {start}")
    extra = len(events) - limit
    if extra > 0:
        lines.append(f"• and {extra} more")
    return "\n".join(lines)


def direct_answer(
    user_msg: str,
    *,
    list_tasks,
    list_events,
    voice_ready: bool,
) -> str | None:
    """Return a tool answer, or None when the message should go to the model."""
    hits = intents_for(user_msg)
    if not hits:
        return None

    parts = []
    if "status" in hits:
        voice_line = (
            "Send a voice note and I answer out loud with ElevenLabs."
            if voice_ready
            else "ElevenLabs voice is not ready on this server yet."
        )
        parts.append(
            "Google Tasks and Calendar are already connected on this bot. "
            "No new Cursor project is required.\n"
            f"{voice_line}"
        )
    if "tasks" in hits:
        tasks = list_tasks() or []
        parts.append(f"Open Google Tasks ({len(tasks)}):\n{_task_lines(tasks)}")
    if "calendar" in hits:
        events = list_events() or []
        parts.append(f"Upcoming calendar ({len(events)}):\n{_event_lines(events)}")
    return "\n\n".join(parts)
