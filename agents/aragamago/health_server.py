"""HTTP health listener so Railway can probe Aragamago without a Telegram round-trip.

This process is a long-polling Telegram bot. Without an HTTP port, Railway
treats the service as dead even when getUpdates is working. Binding PORT and
answering GET /health keeps the replica marked healthy.

This module does not start Telegram polling and does not change production
webhook configuration by itself.
"""

from __future__ import annotations

import json
import logging
import os
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any

from agents.aragamago.talk_page import TALK_PATH, talk_page_html

logger = logging.getLogger(__name__)

HEALTH_PATHS = {"/", "/health", "/healthz"}


def health_payload(telegram_configured: bool | None = None) -> dict[str, Any]:
    if telegram_configured is None:
        telegram_configured = bool(os.environ.get("TELEGRAM_BOT_TOKEN", "").strip())
    return {
        "ok": True,
        "service": "aragamago",
        "role": "telegram-bot",
        "telegram_configured": telegram_configured,
        "polling": True,
        "mode": "health-only" if not telegram_configured else "bot+health",
    }


class HealthHandler(BaseHTTPRequestHandler):
    def do_GET(self) -> None:  # noqa: N802
        path = self.path.split("?", 1)[0]
        if path == TALK_PATH:
            self._write_html(200, talk_page_html())
            return
        if path not in HEALTH_PATHS:
            self._write(404, {"ok": False, "error": "not_found"})
            return
        self._write(200, health_payload())

    def do_HEAD(self) -> None:  # noqa: N802
        path = self.path.split("?", 1)[0]
        code = 200 if path in HEALTH_PATHS else 404
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.end_headers()

    def log_message(self, format: str, *args: Any) -> None:  # noqa: A003
        logger.debug("health %s", format % args)

    def _write(self, code: int, payload: dict[str, Any]) -> None:
        body = json.dumps(payload).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _write_html(self, code: int, page: str) -> None:
        body = page.encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


def resolve_port(port: int | None = None) -> int:
    if port is not None:
        return int(port)
    return int(os.environ.get("PORT") or os.environ.get("ARAGAMAGO_HEALTH_PORT") or "8080")


def start_health_server(port: int | None = None, block: bool = False) -> ThreadingHTTPServer:
    host = os.environ.get("ARAGAMAGO_HEALTH_HOST", "0.0.0.0")
    resolved = resolve_port(port)
    server = ThreadingHTTPServer((host, resolved), HealthHandler)
    logger.info("Aragamago health server listening on %s:%s", host, resolved)
    if block:
        server.serve_forever()
        return server
    thread = threading.Thread(target=server.serve_forever, name="aragamago-health", daemon=True)
    thread.start()
    return server
