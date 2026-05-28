import asyncio
import logging
import time
from typing import Protocol

logger = logging.getLogger(__name__)


class Publisher(Protocol):
    def send(self, text: str) -> None: ...


class TelegramPublisher:
    """Synchronous facade over the async (v20+) python-telegram-bot client.

    Sends plain text (parse_mode=None) — feed titles are untrusted third-party content
    and must not be interpreted as Telegram markup. Errors are logged as type + status
    only, never the raw message/URL (which embeds the bot token).
    """

    def __init__(self, token: str, chat_id: str, send_delay: float = 3.0):
        from telegram import Bot

        self._chat_id = chat_id
        self._send_delay = send_delay
        self._bot = Bot(token)

    def send(self, text: str) -> None:
        from telegram.error import RetryAfter

        async def _send():
            async with self._bot:
                await self._bot.send_message(chat_id=self._chat_id, text=text, parse_mode=None)

        while True:
            try:
                asyncio.run(_send())
                time.sleep(self._send_delay)
                return
            except RetryAfter as exc:
                wait = getattr(exc, "retry_after", 5)
                logger.warning("Telegram rate limit; retrying after %ss", wait)
                time.sleep(float(wait))
            except Exception as exc:  # never log the raw message — it contains the token
                logger.error("Telegram send failed: %s", type(exc).__name__)
                raise
