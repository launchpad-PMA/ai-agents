import logging
import unittest

from agents.aragamago.log_safety import RedactTelegramToken, silence_http_client_urls
from connectors.supabase_connector import host_resolves


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


if __name__ == "__main__":
    unittest.main()
