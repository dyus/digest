from collections.abc import Callable
from dataclasses import dataclass

import feedparser


@dataclass(frozen=True)
class Item:
    title: str
    url: str
    published: str | None = None
    source: str | None = None


def normalize(entry, source: str | None = None) -> Item:
    title = (entry.get("title") or "").strip()
    url = (entry.get("link") or "").strip()
    published = entry.get("published") or entry.get("updated") or None
    return Item(title=title, url=url, published=published, source=source)


def parse_content(content, source: str | None = None) -> list[Item]:
    """Parse already-retrieved feed content (str/bytes) into items, in parse order.

    Pure: no network. Used by tests with fixture content and by fetch_source.
    """
    parsed = feedparser.parse(content)
    return [normalize(entry, source) for entry in parsed.entries]


def fetch_source(source, parser: Callable = feedparser.parse) -> list[Item]:
    """Network retrieval seam for one source. `parser` is injectable for tests.

    May raise on DNS/timeout/HTTP errors — the caller (main.run) isolates per source.
    """
    parsed = parser(source.feed_url)
    return [normalize(entry, source.name) for entry in parsed.entries]
