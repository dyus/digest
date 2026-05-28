from collections.abc import Callable
from dataclasses import dataclass

import feedparser
import httpx

_USER_AGENT = "Mozilla/5.0 (compatible; digest-bot/1.0; +https://github.com/dyus/digest)"


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


def _http_get(url: str) -> bytes:
    resp = httpx.get(
        url,
        headers={"User-Agent": _USER_AGENT},
        follow_redirects=True,
        timeout=30.0,
    )
    resp.raise_for_status()
    return resp.content


def fetch_source(source, http_get: Callable[[str], bytes] = _http_get) -> list[Item]:
    """Fetch one source's feed over HTTP and normalize it. `http_get` is injectable
    for offline tests. Reads the full body via httpx (handles gzip/chunked and sends a
    real User-Agent), avoiding the urllib IncompleteRead some feed servers trigger.

    May raise on DNS/timeout/HTTP errors — the caller (main.run) isolates per source.
    """
    content = http_get(source.feed_url)
    return parse_content(content, source.name)
