import unittest

from agents.aragamago.direct_answers import direct_answer, intents_for


class DirectAnswerTests(unittest.TestCase):
    def test_plain_chat_stays_with_the_model(self):
        self.assertEqual(intents_for("Yo"), set())
        self.assertIsNone(
            direct_answer("Are you working now", list_tasks=lambda: [], list_events=lambda: [], voice_ready=True)
        )

    def test_google_activation_uses_the_live_tools(self):
        reply = direct_answer(
            "tell cursor to activate google task, calendar, and eleven labs voice",
            list_tasks=lambda: [{"title": "Call the temple"}, {"title": "File the brief"}],
            list_events=lambda: [{"summary": "Council", "start": {"dateTime": "2026-11-01T15:00:00Z"}}],
            voice_ready=True,
        )
        self.assertIn("already connected", reply)
        self.assertIn("Call the temple", reply)
        self.assertIn("Council", reply)
        self.assertIn("ElevenLabs", reply)
        self.assertNotIn("Railway Project Setup", reply)

    def test_task_question_does_not_invent_a_project(self):
        reply = direct_answer(
            "what are my tasks",
            list_tasks=lambda: [],
            list_events=lambda: [{"summary": "should not appear"}],
            voice_ready=False,
        )
        self.assertIn("No open Google Tasks.", reply)
        self.assertNotIn("should not appear", reply)


if __name__ == "__main__":
    unittest.main()
