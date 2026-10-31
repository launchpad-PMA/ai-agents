import unittest

from agents.aragamago.provider_keys import direct_openai_model, openrouter_model, resolve_provider_keys


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

    def test_provider_name_is_not_sent_as_the_model(self):
        self.assertEqual(openrouter_model("", "openrouter"), "openrouter/free")
        self.assertEqual(openrouter_model("openrouter", ""), "openrouter/free")
        self.assertEqual(openrouter_model("openrouter/free", "openrouter"), "openrouter/free")
        self.assertEqual(openrouter_model("", "openai/gpt-4.1-mini"), "openai/gpt-4.1-mini")

    def test_openai_model_ignores_openrouter_names(self):
        self.assertEqual(direct_openai_model("", "openrouter"), "gpt-4.1-mini")
        self.assertEqual(direct_openai_model("", "openrouter/free"), "gpt-4.1-mini")
        self.assertEqual(direct_openai_model("gpt-4.1-mini", "openrouter"), "gpt-4.1-mini")


if __name__ == "__main__":
    unittest.main()
