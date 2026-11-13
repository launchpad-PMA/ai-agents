import json
import unittest
from urllib.request import urlopen

from agents.aragamago.health_server import health_payload, resolve_port, start_health_server
from agents.aragamago.talk_page import AGENT_ID, TALK_PATH


class HealthTests(unittest.TestCase):
    def test_payload_reports_missing_token(self):
        payload = health_payload(telegram_configured=False)
        self.assertTrue(payload["ok"])
        self.assertEqual(payload["service"], "aragamago")
        self.assertEqual(payload["mode"], "health-only")
        self.assertFalse(payload["telegram_configured"])

    def test_payload_reports_configured_token(self):
        payload = health_payload(telegram_configured=True)
        self.assertEqual(payload["mode"], "bot+health")
        self.assertTrue(payload["telegram_configured"])

    def test_resolve_port_prefers_explicit(self):
        self.assertEqual(resolve_port(9999), 9999)

    def test_live_health_endpoint(self):
        server = start_health_server(port=0)
        host, port = server.server_address
        try:
            with urlopen(f"http://127.0.0.1:{port}/health", timeout=3) as response:
                body = json.loads(response.read().decode("utf-8"))
                self.assertEqual(response.status, 200)
            self.assertTrue(body["ok"])
            self.assertEqual(body["service"], "aragamago")
            with urlopen(f"http://127.0.0.1:{port}{TALK_PATH}", timeout=3) as talk:
                page = talk.read().decode("utf-8")
                self.assertEqual(talk.status, 200)
                self.assertIn("text/html", talk.headers.get("Content-Type", ""))
            self.assertIn(AGENT_ID, page)
            self.assertIn("elevenlabs-convai", page)
        finally:
            server.shutdown()
            server.server_close()


if __name__ == "__main__":
    unittest.main()
