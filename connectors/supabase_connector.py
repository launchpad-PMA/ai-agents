"""
Supabase Connector — Aragamago
General-purpose database layer for all Aragamago operations.
Reads SUPABASE_URL + SUPABASE_SECRET_KEY via runtime_env.load_local_env()
"""

import os
import logging
import socket
from urllib.parse import urlparse

from runtime_env import load_local_env

logger = logging.getLogger(__name__)

load_local_env()

def resolve_supabase_key(env: dict[str, str] | None = None) -> tuple[str, str]:
    """Return (api_key, mode). Mode is "secret", "publishable", or "missing".

    The database password is not used. The publishable key is enough when the
    conversation_history policies allow the anon role. A secret key is optional.
    """
    source = os.environ if env is None else env
    secret = source.get("SUPABASE_SECRET_KEY") or source.get("SUPABASE_SERVICE_ROLE_KEY") or ""
    publishable = (
        source.get("SUPABASE_PUBLISHABLE_KEY")
        or source.get("SUPABASE_ANON_KEY")
        or source.get("SUPABASE_KEY")
        or ""
    )
    secret = secret.strip()
    publishable = publishable.strip()
    if secret and "your_" not in secret:
        return secret, "secret"
    if publishable and "your_" not in publishable:
        return publishable, "publishable"
    return "", "missing"


SUPABASE_URL = os.environ.get("SUPABASE_URL", "").strip()
SUPABASE_KEY, SUPABASE_KEY_MODE = resolve_supabase_key()

def host_resolves(url: str) -> bool:
    host = urlparse(url).hostname or ""
    if not host:
        return False
    try:
        socket.getaddrinfo(host, 443)
        return True
    except OSError:
        return False


def _supabase_host(url: str) -> str:
    return urlparse(url).hostname or "missing-host"


if not SUPABASE_URL or not SUPABASE_KEY or "your_" in SUPABASE_KEY:
    logger.warning("Supabase not configured — conversation history is off")
    db = None
elif not host_resolves(SUPABASE_URL):
    logger.warning(
        "Supabase host %s does not resolve. Conversation history is off. "
        "The project is paused or deleted. Restore it in the Supabase dashboard, "
        "or set SUPABASE_URL to a live project.",
        _supabase_host(SUPABASE_URL),
    )
    db = None
else:
    from supabase import create_client
    db = create_client(SUPABASE_URL, SUPABASE_KEY)
    logger.info(
        "Supabase connected — %s (%s key, no database password)",
        _supabase_host(SUPABASE_URL),
        SUPABASE_KEY_MODE,
    )


# ── Generic helpers ────────────────────────────────────────────────────────────
def insert(table: str, data: dict) -> dict | None:
    """Insert a row and return the inserted record."""
    if db is None:
        return None
    try:
        result = db.table(table).insert(data).execute()
        return result.data[0] if result.data else None
    except Exception as e:
        logger.error(f"❌ insert({table}): {e}")
        return None


def select(table: str, filters: dict = None, limit: int = 100) -> list:
    """Select rows from a table with optional filters."""
    if db is None:
        return []
    try:
        query = db.table(table).select("*")
        if filters:
            for col, val in filters.items():
                query = query.eq(col, val)
        result = query.limit(limit).execute()
        return result.data or []
    except Exception as e:
        logger.error(f"❌ select({table}): {e}")
        return []


def upsert(table: str, data: dict, on_conflict: str = "id") -> dict | None:
    """Upsert a row (insert or update on conflict)."""
    if db is None:
        return None
    try:
        result = db.table(table).upsert(data, on_conflict=on_conflict).execute()
        return result.data[0] if result.data else None
    except Exception as e:
        logger.error(f"❌ upsert({table}): {e}")
        return None


def delete(table: str, filters: dict) -> bool:
    """Delete rows matching filters."""
    if db is None:
        return False
    try:
        query = db.table(table).delete()
        for col, val in filters.items():
            query = query.eq(col, val)
        query.execute()
        return True
    except Exception as e:
        logger.error(f"❌ delete({table}): {e}")
        return False


def rpc(function_name: str, params: dict = None) -> dict | None:
    """Call a Supabase Edge Function or RPC."""
    if db is None:
        return None
    try:
        result = db.rpc(function_name, params or {}).execute()
        return result.data
    except Exception as e:
        logger.error(f"❌ rpc({function_name}): {e}")
        return None


# ── CLI test ───────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    import sys
    if "--test" in sys.argv:
        print("🗄️  Testing Supabase connection...")
        if db is None:
            print("❌ Supabase not connected — check SUPABASE_URL + SUPABASE_SERVICE_ROLE_KEY in .env")
        else:
            print(f"✅ Connected to: {SUPABASE_URL}")
            print("   Ready for table operations")
