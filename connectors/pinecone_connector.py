"""
Pinecone connector for the BABA_SYSTEM brain.

Index: aragamago-brain, 512 dimensions.
Embeddings go through OpenRouter as openai/text-embedding-3-small.
An OpenRouter key is never sent to api.openai.com.
"""

import os
import logging

from runtime_env import load_local_env

logger = logging.getLogger(__name__)

load_local_env()

PINECONE_API_KEY = os.environ.get("PINECONE_API_KEY", "")
INDEX_NAME = os.environ.get("PINECONE_INDEX_NAME", "aragamago-brain")
INDEX_HOST = os.environ.get("PINECONE_HOST", "https://aragamago-brain-flmynca.svc.aped-4627-b74a.pinecone.io")
EMBEDDING_DIMENSIONS = int(os.environ.get("PINECONE_DIMENSIONS", "512"))
EMBEDDING_MODEL = os.environ.get("EMBEDDING_MODEL", "openai/text-embedding-3-small")

_index = None
_init_tried = False


def _get_index():
    global _index, _init_tried
    if _init_tried:
        return _index
    _init_tried = True
    if not PINECONE_API_KEY or PINECONE_API_KEY.startswith("your_"):
        logger.warning("PINECONE_API_KEY not set — Context Brain offline")
        return None
    try:
        from pinecone import Pinecone
        client = Pinecone(api_key=PINECONE_API_KEY)
        _index = client.Index(host=INDEX_HOST)
        logger.info("Pinecone connected — index %s", INDEX_NAME)
    except Exception as e:
        logger.warning("Brain not available: %s", e)
        _index = None
    return _index


def _embedding_client():
    """Return (client, model) for the key that is actually configured."""
    from openai import OpenAI

    openrouter_key = os.environ.get("OPENROUTER_API_KEY", "").strip()
    openai_key = os.environ.get("OPENAI_API_KEY", "").strip()
    if openai_key.startswith("sk-or-"):
        if not openrouter_key:
            openrouter_key = openai_key
        openai_key = ""
    if openrouter_key:
        return OpenAI(base_url="https://openrouter.ai/api/v1", api_key=openrouter_key, timeout=20), EMBEDDING_MODEL
    if openai_key:
        model = EMBEDDING_MODEL.split("/", 1)[-1]
        return OpenAI(api_key=openai_key, timeout=20), model
    raise RuntimeError("No embedding key configured")


def _embed(text: str) -> list[float]:
    client, model = _embedding_client()
    response = client.embeddings.create(
        model=model,
        input=text,
        dimensions=EMBEDDING_DIMENSIONS,
    )
    return response.data[0].embedding


def upsert_to_brain(doc_id: str, text: str, metadata: dict = None):
    """Embed text and upsert into Pinecone."""
    index = _get_index()
    if index is None:
        logger.error("Pinecone not connected — skipping upsert")
        return False
    try:
        vector = _embed(text)
        index.upsert(vectors=[{
            "id": doc_id,
            "values": vector,
            "metadata": metadata or {},
        }])
        logger.info("Upserted: %s", doc_id)
        return True
    except Exception as e:
        logger.error("Upsert failed for %s: %s", doc_id, e)
        return False


def query_brain(query: str, top_k: int = 5, filter: dict = None) -> list[dict]:
    """Semantic search. Returns a list of {id, score, metadata}."""
    index = _get_index()
    if index is None:
        logger.error("Pinecone not connected — returning empty results")
        return []
    try:
        vector = _embed(query)
        result = index.query(
            vector=vector,
            top_k=top_k,
            include_metadata=True,
            filter=filter,
        )
        matches = []
        for match in result.matches:
            matches.append({
                "id": match.id,
                "score": match.score,
                "metadata": match.metadata,
            })
        return matches
    except Exception as e:
        logger.error("Query failed: %s", e)
        return []


def delete_from_brain(doc_id: str):
    """Remove a document from the index."""
    index = _get_index()
    if index is None:
        return False
    try:
        index.delete(ids=[doc_id])
        logger.info("Deleted: %s", doc_id)
        return True
    except Exception as e:
        logger.error("Delete failed: %s", e)
        return False


if __name__ == "__main__":
    import sys
    if "--test" in sys.argv:
        print("Testing Context Brain connection...")
        index = _get_index()
        if index is None:
            print("Pinecone not connected — check PINECONE_API_KEY")
        else:
            stats = index.describe_index_stats()
            print(f"Connected to '{INDEX_NAME}'")
            print(f"Total vectors: {stats.total_vector_count}")
            print(f"Dimensions: {stats.dimension}")
