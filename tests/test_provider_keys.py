import unittest

from agents.aragamago.provider_keys import openrouter_model, resolve_provider_keys


class ProviderKeyTests(unittest.TestCase):
    def test_openrouter_key_in_openai_slot_is_not_discarded(self):
        router, direct = resolve_provider_keys("", "sk-or-v1-example")
        self.assertEqual(router, "sk-or-v1-example")
        self.assertEqual(direct, "")

    def test_real_openai_key_stays_on_openai(self):
        router, direct = resolve_provider_keys("", "sk-proj-example")
        self.assertEqual(router, "")
        self.assertEqual(direct, "sk-proj-example")

    def test_dedicated_openrouter_key_wins(self):
        router, direct = resolve_provider_keys("sk-or-v1-real", "sk-or-v1-other")
        self.assertEqual(router, "sk-or-v1-real")
        self.assertEqual(direct, "")

    def test_default_model_is_the_original_openrouter_model(self):
        self.assertEqual(openrouter_model("", ""), "google/gemini-2.5-flash")
        self.assertEqual(openrouter_model("openai/gpt-4.1-mini", ""), "openai/gpt-4.1-mini")


if __name__ == "__main__":
    unittest.main()
