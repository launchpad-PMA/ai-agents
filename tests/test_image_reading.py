import unittest

from agents.aragamago.image_reading import gemini_retry_wait_seconds, image_provider_names


class ImageReadingTests(unittest.TestCase):
    def test_gemini_runs_before_the_free_text_pool(self):
        self.assertEqual(
            image_provider_names(["openrouter", "gemini"]),
            ["gemini", "openrouter"],
        )

    def test_order_without_gemini_stays_put(self):
        self.assertEqual(image_provider_names(["openrouter"]), ["openrouter"])

    def test_retry_wait_uses_the_provider_hint(self):
        text = "429 Please retry in 9.210868863s"
        self.assertAlmostEqual(gemini_retry_wait_seconds(text), 9.710868863)

    def test_retry_wait_is_capped(self):
        self.assertEqual(gemini_retry_wait_seconds("429 retry in 120s"), 12.0)

    def test_other_errors_do_not_wait(self):
        self.assertIsNone(gemini_retry_wait_seconds("404 model not found"))


if __name__ == "__main__":
    unittest.main()
