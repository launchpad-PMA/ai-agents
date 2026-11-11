import json
import threading
import unittest
from datetime import datetime
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from tempfile import TemporaryDirectory

from agents.aragamago.local_stack import (
    EMBED_MODEL,
    GENERAL_MODEL,
    NUM_CTX,
    TEMPERATURE,
    VISION_MODEL,
    embed_text,
    local_context,
    ollama_chat,
    relevant_skills,
    search_archive,
    write_archive_note,
)
from agents.aragamago.rooms import ROOMS, staff_directory


class _Capture(BaseHTTPRequestHandler):
    seen = []

    def do_POST(self):  # noqa: N802
        length = int(self.headers.get("Content-Length") or 0)
        payload = json.loads(self.rfile.read(length).decode("utf-8"))
        type(self).seen.append((self.path, payload))
        if self.path == "/api/embed":
            body = {"embeddings": [[0.1, 0.2]]}
        else:
            body = {"message": {"role": "assistant", "content": "Here, Baba."}}
        raw = json.dumps(body).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(raw)))
        self.end_headers()
        self.wfile.write(raw)

    def log_message(self, fmt, *args):
        return


class LocalStackTests(unittest.TestCase):
    def test_models_match_the_talk(self):
        self.assertEqual(GENERAL_MODEL, "qwen3.6:27b")
        self.assertEqual(VISION_MODEL, "qwen3.8:27b")
        self.assertEqual(EMBED_MODEL, "nomic-embed-text")
        self.assertEqual(TEMPERATURE, 0.3)
        self.assertEqual(NUM_CTX, 64000)

    def test_archive_search_and_note(self):
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "dao.md").write_text("The Divine Dao is kept in the sacred library.", encoding="utf-8")
            wrote = write_archive_note(
                "Remember the well depth.",
                root=root,
                now=datetime(2026, 11, 11, 15, 0, 0),
            )
            self.assertTrue(wrote)
            self.assertTrue((root / "inbox" / "20261111150000-remember-the-well-depth.md").is_file())
            found = search_archive("what is the divine dao", root=root)
            self.assertIn("dao.md", found)
            self.assertIn("sacred library", found)

    def test_skill_loads_only_on_its_trigger(self):
        with TemporaryDirectory() as tmp:
            folder = Path(tmp)
            (folder / "propose.md").write_text(
                "# Propose\ntriggers: approve, draft\n\nWait for approval.\n",
                encoding="utf-8",
            )
            self.assertIn("Wait for approval", relevant_skills("please draft the letter", folder=folder))
            self.assertEqual(relevant_skills("what time is it", folder=folder), "")

    def test_ollama_chat_sends_context_and_temperature(self):
        _Capture.seen = []
        server = ThreadingHTTPServer(("127.0.0.1", 0), _Capture)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        host, port = server.server_address
        try:
            reply = ollama_chat(
                "You are Aragamago.",
                "Hello",
                model="qwen3.6:27b",
                base_url=f"http://{host}:{port}",
                timeout=3,
            )
            vector = embed_text("dao", base_url=f"http://{host}:{port}", timeout=3)
        finally:
            server.shutdown()
            server.server_close()
        self.assertEqual(reply, "Here, Baba.")
        self.assertEqual(vector, [0.1, 0.2])
        chat = _Capture.seen[0][1]
        self.assertEqual(chat["model"], "qwen3.6:27b")
        self.assertEqual(chat["options"]["temperature"], 0.3)
        self.assertEqual(chat["options"]["num_ctx"], 64000)
        self.assertFalse(chat["stream"])

    def test_rooms_do_not_bleed_and_are_ours(self):
        titles = [room.title for room in ROOMS]
        self.assertEqual(titles, ["Aragamago", "Maxayauwi"])
        directory = staff_directory()
        self.assertIn("Chief of staff", directory)
        self.assertIn("Maxayauwi", directory)
        for borrowed in ("Freedom Farmers", "Enoch", "NOMAD", "Off-Grid"):
            self.assertNotIn(borrowed, directory)
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "aragamago").mkdir()
            (root / "maxayauwi").mkdir()
            (root / "aragamago" / "dao.md").write_text(
                "The Divine Dao is kept in the sacred library.",
                encoding="utf-8",
            )
            (root / "maxayauwi" / "node.md").write_text(
                "Maxayauwi keeps the RSS3 signer on its own service.",
                encoding="utf-8",
            )
            link = root / "aragamago" / "leak.md"
            link.symlink_to(root / "maxayauwi" / "node.md")
            chief = search_archive("signer service", root=root, room="aragamago")
            self.assertNotIn("signer", chief.lower())
            comm = search_archive("signer service", root=root, room="maxayauwi")
            self.assertIn("RSS3", comm)
            library = search_archive("sacred library", root=root, room="aragamago")
            self.assertIn("dao.md", library)
            shown = local_context("which agents do we have")
        self.assertIn("Aragamago", shown)
        self.assertNotIn("Freedom Farmers", shown)

    def test_missing_server_is_a_skip(self):
        self.assertIsNone(ollama_chat("system", "user", base_url=""))
        self.assertIsNone(embed_text("dao", base_url=""))


if __name__ == "__main__":
    unittest.main()
