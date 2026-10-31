import unittest

from agents.aragamago.chat_memory import clear, recent, remember


class ChatMemoryTests(unittest.TestCase):
    def setUp(self):
        clear()

    def test_new_message_still_sees_the_previous_turn(self):
        remember("1", "user", "My favorite color is green")
        remember("1", "assistant", "Green, noted.")
        remember("1", "user", "What color did I just say?")
        transcript = recent("1")
        self.assertIn("My favorite color is green", transcript)
        self.assertIn("Green, noted.", transcript)
        self.assertIn("What color did I just say?", transcript)

    def test_chats_do_not_share_memory(self):
        remember("1", "user", "only baba")
        self.assertEqual(recent("2"), "")


if __name__ == "__main__":
    unittest.main()
