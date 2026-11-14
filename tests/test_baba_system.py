import io
import tempfile
import unittest
import zipfile
from pathlib import Path

from baba_system.pipeline import (
    chunk_text,
    classify_tier,
    ingest_document,
    seed_system_map,
    vault_note,
)


def _docx(text: str) -> bytes:
    xml = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">'
        f"<w:body><w:p><w:r><w:t>{text}</w:t></w:r></w:p></w:body>"
        "</w:document>"
    )
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w") as archive:
        archive.writestr("word/document.xml", xml)
    return buffer.getvalue()


class BabaSystemTests(unittest.TestCase):
    def test_archive_name_selects_the_archive_tier(self):
        self.assertEqual(classify_tier("Ed Bongo Archive.docx", ""), "archive")
        self.assertEqual(classify_tier("notes.md", "dao embeddings"), "dao")
        self.assertEqual(classify_tier("reading.md", ""), "library")

    def test_chunks_keep_paragraphs_together(self):
        text = "Alpha paragraph.\n\nBeta paragraph."
        self.assertEqual(chunk_text(text), ["Alpha paragraph.\n\nBeta paragraph."])

    def test_vault_note_links_the_system_map(self):
        note = vault_note("Reading", "Body text", "library", "reading.md")
        self.assertIn("[[BABA_SYSTEM]]", note)
        self.assertIn("tier: library", note)
        self.assertIn("Body text", note)

    def test_ingest_writes_the_library_and_indexes_chunks(self):
        stored = []

        def upsert(doc_id, text, metadata):
            stored.append((doc_id, text, metadata))
            return True

        with tempfile.TemporaryDirectory() as folder:
            result = ingest_document(
                "Ed Bongo Archive.docx",
                _docx("Keep the old letters."),
                caption="",
                upsert=upsert,
                root=Path(folder),
            )
        self.assertEqual(result["tier"], "archive")
        self.assertGreater(result["chars"], 0)
        self.assertEqual(result["indexed"], result["chunks"])
        self.assertEqual(stored[0][2]["system"], "BABA_SYSTEM")
        self.assertIn("Keep the old letters.", stored[0][1])

    def test_seed_skips_when_the_map_is_already_stored(self):
        calls = []

        def query(text, top_k=3):
            return [{"id": "baba-system-map", "metadata": {"system": "BABA_SYSTEM"}}]

        def upsert(doc_id, text, metadata):
            calls.append(doc_id)
            return True

        self.assertFalse(seed_system_map(upsert, query))
        self.assertEqual(calls, [])

    def test_markdown_file_passes_through(self):
        stored = []
        with tempfile.TemporaryDirectory() as folder:
            result = ingest_document(
                "dao-notes.md",
                b"# DAO\n\nEmbeddings live here.",
                upsert=lambda doc_id, text, metadata: stored.append(doc_id) or True,
                root=Path(folder),
            )
        self.assertEqual(result["tier"], "dao")
        self.assertTrue(stored)


if __name__ == "__main__":
    unittest.main()
