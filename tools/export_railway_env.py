from __future__ import annotations

from pathlib import Path


MASTER_ENV = Path(
    "/home/baba2-mainoffice/Documents/Obsidian Vault/Agents/Secrets/master.env"
)

# These are the vars the current runtime actually uses in Railway.
RAILWAY_KEYS = [
    "TELEGRAM_BOT_TOKEN",
    "GEMINI_API_KEY",
    "OPENROUTER_API_KEY",
    "ELEVENLABS_API_KEY",
    "ELEVENLABS_VOICE_ID",
    "OPENAI_API_KEY",
    "PINECONE_API_KEY",
    "PINECONE_HOST",
    "PINECONE_INDEX_NAME",
    "SUPABASE_URL",
    "SUPABASE_PUBLISHABLE_KEY",
    "SUPABASE_SECRET_KEY",
    "GOOGLE_SERVICE_ACCOUNT_JSON",
    "GOOGLE_TOKEN_JSON",
    "GOOGLE_SHEET_URL",
    "GOOGLE_CALENDAR_ID",
]

OPTIONAL_EMPTY_OK = {
    "ELEVENLABS_VOICE_ID",
    "GOOGLE_CALENDAR_ID",
}


def parse_env(path: Path) -> dict[str, str]:
    values: dict[str, str] = {}
    for raw_line in path.read_text().splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        values[key.strip()] = value.strip()
    return values


def main() -> int:
    values = parse_env(MASTER_ENV)

    missing = [
        key
        for key in RAILWAY_KEYS
        if not values.get(key, "") and key not in OPTIONAL_EMPTY_OK
    ]

    print("# Paste this block into Railway Variables -> Raw Editor")
    print()
    for key in RAILWAY_KEYS:
        value = values.get(key, "")
        if value or key not in OPTIONAL_EMPTY_OK:
            print(f"{key}={value}")

    if missing:
        print()
        print("# Missing required values:")
        for key in missing:
            print(f"# - {key}")
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
