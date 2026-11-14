"""Mime type for a Telegram voice file, and a check that an ElevenLabs key is usable."""

from pathlib import Path

_MIME = {
    ".mp3": "audio/mpeg",
    ".wav": "audio/wav",
    ".m4a": "audio/mp4",
    ".mp4": "audio/mp4",
    ".webm": "audio/webm",
}


def telegram_voice_mime(path: str) -> str:
    """Telegram voice notes are ogg/opus and have no mime type Gemini can guess."""
    return _MIME.get(Path(path or "").suffix.lower(), "audio/ogg")


def elevenlabs_key_usable(key: str) -> bool:
    """A real ElevenLabs secret starts with sk_. A key id is rejected."""
    return bool(key) and key.startswith("sk_")
