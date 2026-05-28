import logging
import os
import sys

from .config import SOURCES
from .feeds import fetch_source
from .message import format_item
from .publish import TelegramPublisher
from .select import normalize_url, select
from .state import load, save

logger = logging.getLogger(__name__)

DEFAULT_STATE_PATH = "state/seen.json"


def run(sources, publisher, state_path, fetch_fn, *, seed_only: bool = False) -> dict:
    """Fetch all sources (isolating per-source failure), flatten, select once, then
    publish one message per new link. Advance seen-state per send and persist in a
    `finally` so already-sent links survive a mid-run crash (no double-post, no loss).
    """
    seen = load(state_path)

    all_items = []
    keywords_by_source = {}
    for source in sources:
        keywords_by_source[source.name] = source.keywords
        try:
            all_items.extend(fetch_fn(source))
        except Exception as exc:
            logger.error("fetch failed for %s: %s", source.name, type(exc).__name__)
            continue

    selected = select(all_items, seen, keywords_by_source)

    sent = 0
    try:
        for item in selected:
            if not seed_only:
                publisher.send(format_item(item))
                sent += 1
            seen.add(normalize_url(item.url))
    finally:
        save(state_path, seen)

    return {"selected": len(selected), "sent": sent, "seeded": seed_only}


def main() -> int:
    logging.basicConfig(level=logging.INFO)
    seed_only = os.environ.get("SEED_ONLY", "").lower() in ("1", "true", "yes")
    state_path = os.environ.get("STATE_PATH", DEFAULT_STATE_PATH)

    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    chat_id = os.environ.get("TELEGRAM_CHANNEL_ID")
    if not seed_only and (not token or not chat_id):
        logger.error("TELEGRAM_BOT_TOKEN and TELEGRAM_CHANNEL_ID are required")
        return 2

    publisher = None if seed_only else TelegramPublisher(token, chat_id)
    summary = run(SOURCES, publisher, state_path, fetch_source, seed_only=seed_only)
    logger.info("digest run: %s", summary)
    return 0


if __name__ == "__main__":
    sys.exit(main())
