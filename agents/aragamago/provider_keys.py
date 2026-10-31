"""Decide which AI key talks to OpenRouter versus OpenAI directly.

OpenRouter keys look like ``sk-or-...``. The May 2026 "credential hardening"
treated that prefix as "not a real OpenAI key" and then ignored it, so a key
that lived in OPENAI_API_KEY stopped reaching OpenRouter too.
"""

from __future__ import annotations

# Free-model router. "openrouter" alone is the provider name, not a model id.
FREE_ROUTER_MODEL = "openrouter/free"
PROVIDER_NAMES = {"openrouter", "openai", "gemini"}


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


def _is_provider_name(value: str) -> bool:
    return value.strip().lower() in PROVIDER_NAMES


def openrouter_model(explicit: str, shared: str) -> str:
    """Model slug sent to OpenRouter.

    OPENROUTER_MODEL wins. AI_MODEL=openrouter means "use OpenRouter", not a
    model name, so it maps to the free router. A real slug in AI_MODEL, such
    as openai/gpt-4.1-mini, is still honored when OPENROUTER_MODEL is empty.
    """
    explicit = (explicit or "").strip()
    shared = (shared or "").strip()
    if explicit and not _is_provider_name(explicit):
        return explicit
    if shared and not _is_provider_name(shared):
        return shared
    return FREE_ROUTER_MODEL


def direct_openai_model(explicit: str, shared: str) -> str:
    """Model slug for api.openai.com. Ignore provider names and OpenRouter routers."""
    for candidate in ((explicit or "").strip(), (shared or "").strip()):
        if not candidate or _is_provider_name(candidate) or candidate.startswith("openrouter/"):
            continue
        if candidate.startswith("openai/"):
            return candidate.split("/", 1)[1]
        return candidate
    return "gpt-4.1-mini"
