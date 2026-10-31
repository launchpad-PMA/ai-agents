import os
import tempfile
import unittest
from pathlib import Path

from agents.aragamago.obsidian_brain import render_turn, save_turn


class ObsidianBrainTests(unittest.TestCase):
    def test_markup_has_speaker_and_time(self):
        note = render_turn("user", "My favorite color is green", "2026-10-31 09:34 CDT")
        self.assertIn("### 2026-10-31 09:34 CDT", note)
        self.assertIn("**User:** My favorite color is green", note)

    def test_appends_both_turns_to_one_note(self):
        with tempfile.TemporaryDirectory() as folder:
            os.environ["OBSIDIAN_BRAIN_DIR"] = folder
            try:
                self.assertTrue(save_turn("42", "user", "Remember this"))
                self.assertTrue(save_turn("42", "assistant", "Remembered."))
                text = Path(folder, "telegram-42.md").read_text(encoding="utf-8")
            finally:
                os.environ.pop("OBSIDIAN_BRAIN_DIR", None)
        self.assertIn("tags:", text)
        self.assertIn("**User:** Remember this", text)
        self.assertIn("**Aragamago:** Remembered.", text)
        self.assertEqual(text.count("# Telegram 42"), 1)


if __name__ == "__main__":
    unittest.main()