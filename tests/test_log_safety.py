import logging
import unittest

from agents.aragamago.log_safety import RedactTelegramToken, silence_http_client_urls
from connectors.supabase_connector import host_resolves, resolve_supabase_key


class LogSafetyTests(unittest.TestCase):
    def test_redacts_bot_token_in_getupdates_url(self):
        record = logging.LogRecord(
            name="httpx",
            level=logging.INFO,
            pathname=__file__,
            lineno=1,
            msg="HTTP Request: GET https://api.telegram.org/bot123456:AA-FakeToken_example/getUpdates",
            args=(),
            exc_info=None,
        )
        self.assertTrue(RedactTelegramToken().filter(record))
        self.assertNotIn("AA-FakeToken", record.msg)
        self.assertIn("/bot<redacted>/getUpdates", record.msg)

    def test_httpx_logger_is_warning(self):
        silence_http_client_urls()
        self.assertGreaterEqual(logging.getLogger("httpx").level, logging.WARNING)
        self.assertGreaterEqual(logging.getLogger("httpcore").level, logging.WARNING)

    def test_unresolvable_host_is_offline(self):
        self.assertFalse(host_resolves("https://this-project-is-gone.invalid"))

    def test_publishable_key_is_enough_without_secret_or_password(self):
        key, mode = resolve_supabase_key({
            "SUPABASE_PUBLISHABLE_KEY": "sb_publishable_example",
            "SUPABASE_SECRET_KEY": "",
            "DATABASE_PASSWORD": "not-used",
        })
        self.assertEqual(mode, "publishable")
        self.assertEqual(key, "sb_publishable_example")

    def test_supabase_key_name_counts_as_publishable(self):
        key, mode = resolve_supabase_key({"SUPABASE_KEY": "eyJ-example"})
        self.assertEqual(mode, "publishable")
        self.assertTrue(key.startswith("eyJ"))

    def test_secret_key_wins_when_present(self):
        _, mode = resolve_supabase_key({
            "SUPABASE_SECRET_KEY": "sb_secret_example",
            "SUPABASE_PUBLISHABLE_KEY": "sb_publishable_example",
        })
        self.assertEqual(mode, "secret")


if __name__ == "__main__":
    unittest.main()
