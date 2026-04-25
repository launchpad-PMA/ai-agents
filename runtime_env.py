"""
Shared environment loading rules for local development vs Railway runtime.

Rules:
- On Railway, rely on injected environment variables only.
- Locally, load the canonical machine secrets file unless ENV_PATH overrides it.
"""

from __future__ import annotations

import os


DEFAULT_LOCAL_ENV_PATH = (
    "/home/baba2-mainoffice/Documents/Obsidian Vault/Agents/Secrets/master.env"
)
LOCAL_ONLY_SKIP_KEYS = {
    # Runtime markers should come from the real environment, not from a pasted secrets file.
    "RAILWAY_STATIC_URL",
}


def is_railway() -> bool:
    return bool(os.environ.get("RAILWAY_STATIC_URL"))


def clean_env_value(value: str) -> str:
    value = value.strip()
    if len(value) >= 2 and (
        (value[0] == value[-1] == '"') or (value[0] == value[-1] == "'")
    ):
        return value[1:-1]
    return value


def get_env_path() -> str:
    return os.environ.get("ENV_PATH", DEFAULT_LOCAL_ENV_PATH)


def load_local_env() -> None:
    if is_railway():
        return

    env_path = get_env_path()
    try:
        with open(env_path) as f:
            for line in f:
                line = line.strip()
                if "=" in line and not line.startswith("#"):
                    key, value = line.split("=", 1)
                    key = key.strip()
                    if key in LOCAL_ONLY_SKIP_KEYS:
                        continue
                    cleaned_value = clean_env_value(value)
                    # Treat empty preexisting values as unset so local secrets still load.
                    if not os.environ.get(key):
                        os.environ[key] = cleaned_value
    except FileNotFoundError:
        pass