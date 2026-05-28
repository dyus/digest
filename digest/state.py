import json
from pathlib import Path
from urllib.parse import urlsplit

MAX_URL_LEN = 2048


def is_valid_url(url: str) -> bool:
    """Only http(s), no userinfo (no credentials in committed history), bounded length."""
    if not url or len(url) > MAX_URL_LEN:
        return False
    try:
        parts = urlsplit(url)
    except ValueError:
        return False
    if parts.scheme not in ("http", "https"):
        return False
    if not parts.netloc or "@" in parts.netloc:
        return False
    return True


def load(path) -> set[str]:
    p = Path(path)
    if not p.exists():
        return set()
    return set(json.loads(p.read_text()))


def save(path, urls) -> None:
    """Write sorted JSON for stable, reviewable diffs. Invalid URLs never persisted."""
    valid = sorted(u for u in urls if is_valid_url(u))
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(valid, indent=2) + "\n")
