"""Ingest a document into the BABA_SYSTEM library and the Pinecone brain.

Tiers match the diagram:
- library: the working Markdown set
- archive: the Ed Bongo archive
- dao: dao and embedding notes

Dropbox, Google Drive, and iCloud stay the folders you sync. This module
writes the library on disk when a root is set, and stores the searchable
chunks in Pinecone. A failed index write does not raise into the chat reply.
"""

from __future__ import annotations

import os
import re
from datetime import datetime, timezone
from pathlib import Path

from baba_system.convert import convert_to_markdown

SYSTEM_NOTE = """---
title: BABA_SYSTEM
tier: library
system: BABA_SYSTEM
---

# BABA_SYSTEM

Raw documents (docx, pdf, md, txt) become Markdown. Docx goes through Pandoc when Pandoc is installed. Pdf text is extracted in the bot.

The library has three tiers:

- library: the working set
- archive: the Ed Bongo archive
- dao: dao notes and the embedding set

Each note is Markdown and links to [[BABA_SYSTEM]]. The Obsidian vault is that Markdown. Pinecone index aragamago-brain stores one vector per chunk so Aragamago can search it.

A normal Telegram reply still goes out when Pinecone or the file write fails. Chat turns are not copied into the vault. A file is stored when you send the file, or when you say "remember that".

Dropbox, Google Drive, and iCloud are the folders you already sync. Point BABA_SYSTEM_ROOT at one of those folders on a machine that syncs them. On Railway the disk copy is temporary. The Pinecone chunks are the copy that survives a restart.
"""

_CHUNK_CHARS = 1000
_SEED_ID = "baba-system-map"


def library_root() -> Path:
    explicit = os.environ.get("BABA_SYSTEM_ROOT", "").strip()
    if explicit:
        return Path(explicit)
    if os.environ.get("RAILWAY_ENVIRONMENT") or os.environ.get("RAILWAY_STATIC_URL"):
        return Path("/tmp/baba-system")
    return Path(__file__).resolve().parent / "library"


def classify_tier(filename: str, caption: str = "") -> str:
    text = f"{filename} {caption}".lower()
    if "archive" in text or "ed bongo" in text:
        return "archive"
    if "dao" in text:
        return "dao"
    return "library"


def chunk_text(text: str, size: int = _CHUNK_CHARS) -> list[str]:
    body = (text or "").strip()
    if not body:
        return []
    paragraphs = [part.strip() for part in re.split(r"\n\s*\n", body) if part.strip()]
    chunks: list[str] = []
    current = ""
    for paragraph in paragraphs:
        if len(paragraph) > size:
            if current:
                chunks.append(current)
                current = ""
            for start in range(0, len(paragraph), size):
                chunks.append(paragraph[start:start + size])
            continue
        candidate = f"{current}\n\n{paragraph}".strip() if current else paragraph
        if len(candidate) <= size:
            current = candidate
        else:
            chunks.append(current)
            current = paragraph
    if current:
        chunks.append(current)
    return chunks


def vault_note(title: str, body: str, tier: str, filename: str) -> str:
    safe_title = title.replace("\n", " ").strip() or filename
    return (
        "---\n"
        f"title: {safe_title}\n"
        f"tier: {tier}\n"
        "system: BABA_SYSTEM\n"
        f"source: {filename}\n"
        "---\n\n"
        f"# {safe_title}\n\n"
        f"{body.strip()}\n\n"
        "Related: [[BABA_SYSTEM]]\n"
    )


def _slug(filename: str) -> str:
    stem = Path(filename or "document").stem.lower()
    slug = re.sub(r"[^a-z0-9]+", "-", stem).strip("-")
    return (slug or "document")[:40]


def _write_library(root: Path, filename: str, data: bytes, note: str, tier: str) -> dict:
    raw_dir = root / "raw"
    processed_dir = root / "processed"
    vault_dir = root / "vault" / tier
    archive_dir = root / "archive"
    for folder in (raw_dir, processed_dir, vault_dir, archive_dir):
        folder.mkdir(parents=True, exist_ok=True)
    slug = _slug(filename)
    raw_path = raw_dir / f"{slug}-{Path(filename).suffix.lstrip('.') or 'bin'}"
    raw_path.write_bytes(data)
    processed_path = processed_dir / f"{slug}.md"
    processed_path.write_text(note, encoding="utf-8")
    vault_path = vault_dir / f"{slug}.md"
    vault_path.write_text(note, encoding="utf-8")
    if tier == "archive":
        (archive_dir / raw_path.name).write_bytes(data)
    return {
        "raw": str(raw_path),
        "processed": str(processed_path),
        "vault": str(vault_path),
    }


def ingest_document(filename: str, data: bytes, caption: str = "", upsert=None, root: Path | None = None) -> dict:
    """Convert one file, write the vault note, and index the chunks."""
    markdown = convert_to_markdown(filename, data)
    tier = classify_tier(filename, caption)
    title = Path(filename or "document").stem
    note = vault_note(title, markdown, tier, filename or "document")
    library = root if root is not None else library_root()
    paths = _write_library(library, filename or "document", data, note, tier)
    chunks = chunk_text(note)
    indexed = 0
    slug = _slug(filename or "document")
    stamp = datetime.now(timezone.utc).isoformat()
    for index, chunk in enumerate(chunks):
        doc_id = f"baba-{tier}-{slug}-{index}"
        metadata = {
            "text": chunk[:4000],
            "source": "baba-system",
            "tier": tier,
            "filename": (filename or "document")[:200],
            "date": stamp,
            "system": "BABA_SYSTEM",
        }
        if upsert and upsert(doc_id, chunk, metadata):
            indexed += 1
    return {
        "filename": filename or "document",
        "tier": tier,
        "chars": len(note),
        "chunks": len(chunks),
        "indexed": indexed,
        "paths": paths,
    }


def ingest_report(result: dict) -> str:
    return (
        f"Stored {result['filename']} in the {result['tier']} tier.\n"
        f"Markdown characters: {result['chars']}. Chunks: {result['chunks']}. "
        f"Indexed: {result['indexed']}."
    )


def seed_system_map(upsert, query) -> bool:
    """Index the system map once. Skip when that note is already stored."""
    if query is None or upsert is None:
        return False
    try:
        matches = query("BABA_SYSTEM hub pandoc pinecone obsidian", top_k=3) or []
    except Exception:
        matches = []
    for match in matches:
        metadata = match.get("metadata") or {}
        if metadata.get("system") == "BABA_SYSTEM" and _SEED_ID in str(match.get("id", "")):
            return False
    metadata = {
        "text": SYSTEM_NOTE[:4000],
        "source": "baba-system",
        "tier": "library",
        "filename": "BABA_SYSTEM.md",
        "date": datetime.now(timezone.utc).isoformat(),
        "system": "BABA_SYSTEM",
    }
    return bool(upsert(_SEED_ID, SYSTEM_NOTE, metadata))
