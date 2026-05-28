# Dependencies

Key dependency choices and rationale. Versions are pinned exactly in `requirements.txt` (runtime) and `requirements-dev.txt` (dev). Grounded in `CLAUDE.md` product shape and real usage in source.

## Runtime

### `feedparser==6.0.11`
- **Used by:** [[feeds]] (`digest/feeds.py` — `feedparser.parse`).
- **Why:** De-facto standard for parsing RSS/Atom in Python. Tolerant of malformed feeds and the format drift across the MVP sources (Mux, Bitmovin, Cloudflare, Demuxed / The Broadcast Knowledge), so we don't hand-roll XML handling per source.
- **Note:** Injected as the default `parser` callable in `fetch_source(...)`, which keeps the dependency mockable in tests rather than hard-wired.

### `python-telegram-bot==21.9`
- **Used by:** [[publish]] (`digest/publish.py` — `telegram.Bot`, `telegram.error.RetryAfter`).
- **Why:** Maintained, well-documented Telegram Bot API wrapper. Gives us `Bot.send_message` plus typed errors (notably `RetryAfter` for rate-limit backoff) instead of raw HTTP calls. Matches the "one message per link" publish model.
- **Note:** v21.x is async-first; `publish.py` drives it via an async send wrapped per message. Imported lazily inside the publisher so non-publish code paths (and tests) don't require it at import time.

## Dev

### `pytest==9.0.2`
- **Used by:** `tests/` acceptance suite and the `evals/` harness.
- **Why:** Standard Python test runner; the dev loop (stages 4–5 in `CLAUDE.md`) is TDD against pytest acceptance tests plus an LLM-judge eval harness.

## Choices deliberately avoided

- **No dependency/lock manager (poetry, pip-tools, uv):** MVP keeps a flat pinned `requirements.txt` for simplicity and fast GitHub Actions installs. Revisit if the tree grows.
- **No HTTP client (requests/httpx) as a direct dep:** feed fetching goes through feedparser; Telegram I/O goes through python-telegram-bot. No separate HTTP layer needed yet.

See [[architecture]] for where these sit in the pipeline. Open questions on dependency policy live in [[gaps]].
