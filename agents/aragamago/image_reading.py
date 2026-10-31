"""Choose a vision provider and decide how long to wait after a Gemini 429."""

GEMINI_IMAGE_FALLBACK = "gemini-3.5-flash-lite"
_RETRY_CAP_SECONDS = 12.0
_DEFAULT_RETRY_SECONDS = 10.0


def image_provider_names(order):
    """Try Gemini before the free text pool when both are configured."""
    names = []
    for provider in order or []:
        provider = (provider or "").strip().lower()
        if provider in ("gemini", "openrouter", "openai") and provider not in names:
            names.append(provider)
    if "gemini" in names:
        names.remove("gemini")
        names.insert(0, "gemini")
    return names


def gemini_retry_wait_seconds(error_text):
    """Return a short wait after a rate-limit error, or None for other errors."""
    text = error_text or ""
    lower = text.lower()
    limited = "429" in text or "quota" in lower or "rate limit" in lower or "rate-limit" in lower
    if not limited:
        return None
    import re

    match = re.search(r"retry in ([0-9]+(?:\.[0-9]+)?)\s*s", text, re.IGNORECASE)
    if not match:
        match = re.search(r"seconds:\s*([0-9]+(?:\.[0-9]+)?)", text, re.IGNORECASE)
    if not match:
        return _DEFAULT_RETRY_SECONDS
    return min(float(match.group(1)) + 0.5, _RETRY_CAP_SECONDS)
