"""
Supabase Connector — Aragamago
General-purpose database layer for all Aragamago operations.
Reads SUPABASE_URL + SUPABASE_SERVICE_ROLE_KEY from .env
"""

import os
import logging

logger = logging.getLogger(__name__)

# ── Load env ───────────────────────────────────────────────────────────────────
def _load_env():
    env_path = os.environ.get("ENV_PATH", r"C:\Users\Baba\Documents\antigravity\.env")
    try:
        with open(env_path) as f:
            for line in f:
                line = line.strip()
                if "=" in line and not line.startswith("#"):
                    k, v = line.split("=", 1)
                    os.environ.setdefault(k.strip(), v.strip())
    except FileNotFoundError:
        pass

_load_env()

SUPABASE_URL = os.environ.get("SUPABASE_URL", "")
# Support both new naming (publishable/secret) and legacy (anon/service_role)
SUPABASE_KEY = (
    os.environ.get("SUPABASE_SECRET_KEY") or          # new name for service_role
    os.environ.get("SUPABASE_SERVICE_ROLE_KEY") or    # legacy
    os.environ.get("SUPABASE_PUBLISHABLE_KEY") or     # new name for anon
    os.environ.get("SUPABASE_ANON_KEY") or            # legacy
    ""
)

if not SUPABASE_URL or not SUPABASE_KEY or "your_" in SUPABASE_KEY:
    logger.warning("⚠️  Supabase not configured — DB offline")
    db = None
else:
    from supabase import create_client
    db = create_client(SUPABASE_URL, SUPABASE_KEY)
    logger.info(f"✅ Supabase connected — {SUPABASE_URL}")


# ── Generic helpers ────────────────────────────────────────────────────────────
def insert(table: str, data: dict) -> dict | None:
    """Insert a row and return the inserted record."""
    if db is None:
        logger.error("Supabase not connected")
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
