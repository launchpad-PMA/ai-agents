"""Keep secrets out of process logs.

python-telegram-bot uses httpx, and httpx logs every request URL at INFO.
Telegram puts the bot token in that URL (`/bot<token>/getUpdates`), so INFO
logs are enough to take over the bot. The httpx logger stays at WARNING, and
a filter redacts any token that still reaches a message.
"""

from __future__ import annotations

import logging
import re

_BOT_TOKEN = re.compile(r"/bot\d+:[A-Za-z0-9_-]+")


class RedactTelegramToken(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        if isinstance(record.msg, str):
            record.msg = _BOT_TOKEN.sub("/bot<redacted>", record.msg)
        if record.args:
            args = record.args if isinstance(record.args, tuple) else (record.args,)
            record.args = tuple(
                _BOT_TOKEN.sub("/bot<redacted>", arg) if isinstance(arg, str) else arg
                for arg in args
            )
        return True


def silence_http_client_urls() -> None:
    for name in ("httpx", "httpcore"):
        logging.getLogger(name).setLevel(logging.WARNING)
    logging.getLogger().addFilter(RedactTelegramToken())
