"""
Pinecone Connector — Context Brain
Aragamago ecosystem: semantic memory layer.

Usage:
  from connectors.pinecone_connector import query_brain, upsert_to_brain

Reads PINECONE_API_KEY from environment.
Index: aragamago-brain (text-embedding-3-small, 1536 dims)
"""

import os
import logging

logger = logging.getLogger(__name__)

# ── Load env ───────────────────────────────────────────────────────────────────
def _load_env():
    env = {}
    env_path = os.environ.get("ENV_PATH", r"C:\Users\Baba\Documents\antigravity\.env")
    try:
        with open(env_path) as f:
            for line in f:
                line = line.strip()
                if "=" in line and not line.startswith("#"):
                    k, v = line.split("=", 1)
                    env[k.strip()] = v.strip()
    except FileNotFoundError:
        pass
    # Railway / Supabase injects env vars directly — os.environ takes priority
    for k, v in env.items():
        os.environ.setdefault(k, v)

_load_env()

PINECONE_API_KEY = os.environ.get("PINECONE_API_KEY", "")
INDEX_NAME = os.environ.get("PINECONE_INDEX_NAME", "aragamago-brain")
INDEX_HOST = os.environ.get("PINECONE_HOST", "https://aragamago-brain-flmynca.svc.aped-4627-b74a.pinecone.io")

if not PINECONE_API_KEY or PINECONE_API_KEY.startswith("your_"):
    logger.warning("⚠️  PINECONE_API_KEY not set — Context Brain offline")
    _pc = None
    _index = None
else:
    from pinecone import Pinecone
    _pc = Pinecone(api_key=PINECONE_API_KEY)
    _index = _pc.Index(host=INDEX_HOST)  # direct host = faster, no lookup needed
    logger.info(f"✅ Pinecone connected — host: {INDEX_HOST}")


# ── Embed via OpenAI ───────────────────────────────────────────────────────────
def _embed(text: str) -> list[float]:
    """Generate embedding using OpenAI text-embedding-3-small (512 dims to match index)."""
    from openai import OpenAI
    client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY", ""))
    response = client.embeddings.create(
        model="text-embedding-3-small",
        input=text,
        dimensions=512  # matches aragamago-brain index dimension
    )
    return response.data[0].embedding


# ── Public API ─────────────────────────────────────────────────────────────────
def upsert_to_brain(doc_id: str, text: str, metadata: dict = None):
    """
    Embed text and upsert into Pinecone.
    metadata: dict with keys like source, tier, date, tags
    """
    if _index is None:
        logger.error("Pinecone not connected — skipping upsert")
        return False
    try:
        vector = _embed(text)
        _index.upsert(vectors=[{
            "id": doc_id,
            "values": vector,
            "metadata": metadata or {}
        }])
        logger.info(f"✅ Upserted: {doc_id}")
        return True
    except Exception as e:
        logger.error(f"❌ Upsert failed for {doc_id}: {e}")
        return False


def query_brain(query: str, top_k: int = 5, filter: dict = None) -> list[dict]:
    """
    Semantic search: embed query → find top_k closest docs.
    Returns list of {id, score, metadata} dicts.
    """
    if _index is None:
        logger.error("Pinecone not connected — returning empty results")
        return []
    try:
        vector = _embed(query)
        result = _index.query(
            vector=vector,
            top_k=top_k,
            include_metadata=True,
            filter=filter
        )
        matches = []
        for match in result.matches:
            matches.append({
                "id": match.id,
                "score": match.score,
                "metadata": match.metadata
            })
        return matches
    except Exception as e:
        logger.error(f"❌ Query failed: {e}")
        return []


def delete_from_brain(doc_id: str):
    """Remove a document from the index."""
    if _index is None:
        return False
    try:
        _index.delete(ids=[doc_id])
        logger.info(f"🗑️  Deleted: {doc_id}")
        return True
    except Exception as e:
        logger.error(f"❌ Delete failed: {e}")
        return False


# ── CLI test ───────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    import sys
    if "--test" in sys.argv:
        print("🧠 Testing Context Brain connection...")
        if _index is None:
            print("❌ Pinecone not connected — check PINECONE_API_KEY in .env")
        else:
            stats = _index.describe_index_stats()
            print(f"✅ Connected to '{INDEX_NAME}'")
            print(f"   Total vectors: {stats.total_vector_count}")
            print(f"   Dimensions: {stats.dimension}")
