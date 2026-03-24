#!/usr/bin/env python3
"""
Expand ${VAR} placeholders in rss3-node config/config.yaml from a sibling .env file.
RSS3 node v2.x does not substitute env vars inside the mounted YAML; Docker only passes
env into the process — the URI string must be concrete in the file the node reads.

Usage (on Linode, from rss3-node directory):
  python3 render-rss3-node-config-from-env.py
  docker-compose down && docker-compose up -d

Paths default to ./config/config.yaml and ./.env next to cwd.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path


def load_env(path: Path) -> dict[str, str]:
    out: dict[str, str] = {}
    for line in path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, _, v = line.partition("=")
        out[k.strip()] = v
    return out


def main() -> int:
    root = Path.cwd()
    env_path = root / ".env"
    cfg_path = root / "config" / "config.yaml"
    if not env_path.is_file():
        print("Missing .env", file=sys.stderr)
        return 1
    if not cfg_path.is_file():
        print("Missing config/config.yaml", file=sys.stderr)
        return 1
    env = load_env(env_path)
    raw = cfg_path.read_text()

    def repl(m: re.Match[str]) -> str:
        key = m.group(1)
        if key in env:
            return env[key]
        return m.group(0)

    out = re.sub(r"\$\{([A-Za-z0-9_]+)\}", repl, raw)
    if "${" in out:
        print(
            "Warning: unresolved ${...} placeholders remain; check .env",
            file=sys.stderr,
        )
    cfg_path.write_text(out)
    print(f"Wrote {cfg_path} with env substitution.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
