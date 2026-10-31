"""Decide which AI key talks to OpenRouter versus OpenAI directly.

OpenRouter keys look like ``sk-or-...``. The May 2026 "credential hardening"
treated that prefix as "not a real OpenAI key" and then ignored it, so a key
that lived in OPENAI_API_KEY stopped reaching OpenRouter too.
"""

from __future__ import annotations

# Model used by the first OpenRouter fallback (Apr 16, 2026), before the
# Apr 27 routing change defaulted OpenRouter to openai/gpt-4.1-mini.
ORIGINAL_OPENROUTER_MODEL = "google/gemini-2.5-flash"


def is_openrouter_key(value: str) -> bool:
    return bool(value) and value.startswith("sk-or-")


def resolve_provider_keys(openrouter_key: str, openai_key: str) -> tuple[str, str]:
    """Return (openrouter_key, direct_openai_key).

    An OpenRouter-shaped key in OPENAI_API_KEY is used for OpenRouter when
    OPENROUTER_API_KEY is empty. It is never sent to api.openai.com.
    """
    openrouter_key = (openrouter_key or "").strip()
    openai_key = (openai_key or "").strip()
    if not openrouter_key and is_openrouter_key(openai_key):
        return openai_key, ""
    if is_openrouter_key(openai_key):
        return openrouter_key, ""
    return openrouter_key, openai_key


def openrouter_model(explicit: str, shared: str) -> str:
    """Prefer an explicit model. Otherwise use the original OpenRouter model."""
    chosen = (explicit or "").strip() or (shared or "").strip()
    return chosen or ORIGINAL_OPENROUTER_MODEL
