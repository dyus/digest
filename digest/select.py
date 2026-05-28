from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

# Strip ONLY known tracking params. Never strip unknown params or the whole query —
# over-collapsing distinct articles (e.g. WordPress ?p=1 vs ?p=2) silently drops links.
_TRACKING_PREFIXES = ("utm_",)
_TRACKING_EXACT = {"fbclid", "gclid", "ref", "mc_cid"}


def _is_tracking(key: str) -> bool:
    return key in _TRACKING_EXACT or any(key.startswith(p) for p in _TRACKING_PREFIXES)


def normalize_url(url: str) -> str:
    """Dedup key: drop tracking params, trailing slash, and fragment. Bias to under-collapse."""
    parts = urlsplit(url)
    kept = [(k, v) for k, v in parse_qsl(parts.query, keep_blank_values=True) if not _is_tracking(k)]
    path = parts.path.rstrip("/") or "/"
    return urlunsplit((parts.scheme, parts.netloc, path, urlencode(kept), ""))


def _matches_keywords(item, keywords) -> bool:
    if not keywords:
        return True
    title = (item.title or "").lower()
    return any(k.lower() in title for k in keywords)


def select(items, seen, keywords_by_source=None):
    """From flattened, source-tagged items + seen-set, return new, deduped (incl.
    cross-source), keyword-filtered items in input order.
    """
    keywords_by_source = keywords_by_source or {}
    result = []
    seen_in_run: set[str] = set()
    for item in items:
        key = normalize_url(item.url)
        if key in seen or key in seen_in_run:
            continue
        if not _matches_keywords(item, keywords_by_source.get(item.source)):
            continue
        seen_in_run.add(key)
        result.append(item)
    return result
