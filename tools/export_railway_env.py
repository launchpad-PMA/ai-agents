from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

from runtime_env import clean_env_value, get_env_path

ENV_TEMPLATE = REPO_ROOT / ".env.example"
SECTION_START = "# 2. ARAGAMAGO"
SECTION_END = "# 3. "
AI_KEYS = ("OPENROUTER_API_KEY", "OPENAI_API_KEY", "GEMINI_API_KEY")


def template_keys(path: Path = ENV_TEMPLATE) -> list[str]:
    """Aragamago keys, read from the single .env.example so this list is never duplicated."""
    keys: list[str] = []
    in_section = False
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if line.startswith(SECTION_START):
            in_section = True
            continue
        if in_section and line.startswith(SECTION_END):
            break
        if in_section and "=" in line and not line.startswith("#"):
            keys.append(line.split("=", 1)[0].strip())
    return keys


def parse_env(path: Path) -> dict[str, str]:
    values: dict[str, str] = {}
    for raw_line in path.read_text().splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        values[key.strip()] = clean_env_value(value.split(" #", 1)[0])
    return values


def main() -> int:
    values = parse_env(Path(get_env_path()))
    keys = template_keys()

    missing = []
    if not values.get("TELEGRAM_BOT_TOKEN"):
        missing.append("TELEGRAM_BOT_TOKEN")
    if not any(values.get(key) for key in AI_KEYS):
        missing.append("one of " + ", ".join(AI_KEYS))

    print("# Paste this block into Railway Variables -> Raw Editor")
    print()
    for key in keys:
        value = values.get(key, "")
        if value:
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
