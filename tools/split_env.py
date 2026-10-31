"""Split an old .env (e.g. antigravity\\.env) into the two local secrets files.

    bot  -> master.env            (Aragamago Telegram bot + JARVIS; read by runtime_env)
    rss3 -> rss3-node-linode.env  (RSS3 node + Maxayauwi; read by agents/aragamago/rss3_tools.py)

Which key goes where comes from the sections in .env.example. Existing target files are
merged, never overwritten: a key already present keeps its current value and any
mismatch is reported by name. Only key names are printed — never values.
The source file is not modified or deleted.

Usage:
    python tools/split_env.py SOURCE_ENV [OUT_DIR]

OUT_DIR defaults to the directory of SOURCE_ENV.
"""

from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

from runtime_env import clean_env_value

ENV_TEMPLATE = REPO_ROOT / ".env.example"
BOT_FILE = "master.env"
RSS3_FILE = "rss3-node-linode.env"
CURSOR_ONLY = {"RAILWAY_API_TOKEN"}
RSS3_PREFIXES = ("NODE_", "RSS3_", "NEYNAR_")


def section_keys(path: Path = ENV_TEMPLATE) -> dict[str, str]:
    """Map each template key to 'bot', 'rss3', or 'cursor'."""
    owner: dict[str, str] = {}
    section = ""
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if line.startswith("# 1. "):
            section = "cursor"
        elif line.startswith("# 2. ") or line.startswith("# 4. "):
            section = "bot"
        elif line.startswith("# 3. "):
            section = "rss3"
        elif "=" in line and not line.startswith("#") and section:
            key = line.split("=", 1)[0].strip()
            target = "rss3" if key.startswith(RSS3_PREFIXES) else section
            owner.setdefault(key, target)
    return owner


def read_env(path: Path) -> dict[str, str]:
    values: dict[str, str] = {}
    if not path.exists():
        return values
    for raw in path.read_text(encoding="utf-8-sig").splitlines():
        line = raw.strip()
        if line.startswith("export "):
            line = line[len("export "):]
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        values[key.strip()] = clean_env_value(value)
    return values


def classify(key: str, owner: dict[str, str]) -> str:
    if key in CURSOR_ONLY:
        return "cursor"
    if key in owner:
        return owner[key]
    if key.startswith(RSS3_PREFIXES) or key in {"DB_CONNECTION", "DATABASE_URI"}:
        return "rss3"
    return "unsorted"


def merge_into(target: Path, incoming: dict[str, str], header: str) -> dict[str, list[str]]:
    existing = read_env(target)
    report = {"added": [], "same": [], "conflict": []}
    new_lines: list[str] = []
    for key, value in incoming.items():
        if not value:
            continue
        if key not in existing:
            report["added"].append(key)
            new_lines.append(f"{key}={value}")
        elif existing[key] == value:
            report["same"].append(key)
        else:
            report["conflict"].append(key)
    if new_lines:
        target.parent.mkdir(parents=True, exist_ok=True)
        has_content = target.exists() and target.stat().st_size > 0
        prefix = "\n" if has_content else f"# {header}\n# Local only. Never commit.\n"
        with target.open("a", encoding="utf-8") as handle:
            handle.write(prefix + "\n".join(new_lines) + "\n")
    return report


def main(argv: list[str]) -> int:
    if len(argv) < 2:
        print(__doc__)
        return 2
    source = Path(argv[1]).expanduser()
    if not source.exists():
        print(f"Source not found: {source}")
        return 1
    out_dir = Path(argv[2]).expanduser() if len(argv) > 2 else source.parent

    owner = section_keys()
    values = read_env(source)
    buckets: dict[str, dict[str, str]] = {"bot": {}, "rss3": {}, "cursor": {}, "unsorted": {}}
    for key, value in values.items():
        buckets[classify(key, owner)][key] = value

    # Unknown keys go to the bot file so nothing is lost; they are listed for review.
    bot_incoming = {**buckets["bot"], **buckets["unsorted"]}
    bot_report = merge_into(out_dir / BOT_FILE, bot_incoming, "Aragamago bot + JARVIS secrets")
    rss3_report = merge_into(out_dir / RSS3_FILE, buckets["rss3"], "RSS3 node + Maxayauwi secrets")

    empty = [key for key, value in values.items() if not value]
    print(f"Read {len(values)} keys from {source}")
    for label, name, report in (("BOT", BOT_FILE, bot_report), ("RSS3", RSS3_FILE, rss3_report)):
        print(f"\n{label} -> {out_dir / name}")
        print(f"  added:    {', '.join(report['added']) or '-'}")
        print(f"  already there (same value): {', '.join(report['same']) or '-'}")
        if report["conflict"]:
            print(f"  CONFLICT (kept existing value, check by hand): {', '.join(report['conflict'])}")
    if buckets["unsorted"]:
        print(f"\nNot in .env.example (put in {BOT_FILE}, review): {', '.join(buckets['unsorted'])}")
    if buckets["cursor"]:
        print(f"\nCursor-only (add in Cursor Secrets, not written): {', '.join(buckets['cursor'])}")
    if empty:
        print(f"\nEmpty in source (skipped): {', '.join(empty)}")
    print("\nSource file was not changed. Delete it yourself once the two files look right.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
