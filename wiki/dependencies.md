# Dependencies

Key dependency choices and rationale. Source of truth is `pyproject.toml` (declared deps) + `uv.lock` (exact resolved versions). Runtime deps are pinned exactly; dev deps use floors (`>=`) and are locked transitively. Grounded in `CLAUDE.md` product shape and real usage in source.

## Runtime

### `feedparser==6.0.11`
- **Used by:** [[feeds]] (`digest/feeds.py` — `feedparser.parse`).
- **Why:** De-facto standard for parsing RSS/Atom in Python. Tolerant of malformed feeds and the format drift across the MVP sources (Mux, Bitmovin, Cloudflare, Demuxed / The Broadcast Knowledge), so we don't hand-roll XML handling per source.
- **Note:** Injected as the default `parser` callable in `fetch_source(...)`, which keeps the dependency mockable in tests rather than hard-wired.

### `python-telegram-bot==21.9`
- **Used by:** [[publish]] (`digest/publish.py` — `telegram.Bot`, `telegram.error.RetryAfter`).
- **Why:** Maintained, well-documented Telegram Bot API wrapper. Gives us `Bot.send_message` plus typed errors (notably `RetryAfter` for rate-limit backoff) instead of raw HTTP calls. Matches the "one message per link" publish model.
- **Note:** v21.x is async-first; `publish.py` drives it via an async send wrapped per message. Imported lazily inside the publisher so non-publish code paths (and tests) don't require it at import time. (Pulls in `httpx` transitively, but we now declare it directly too — see below.)

### `httpx>=0.27`
- **Used by:** [[feeds]] (`digest/feeds.py` — `_http_get` fetches each feed body before handing it to feedparser).
- **Why:** Added in `fix: robust httpx feed fetch` (commit `e746c06`) to replace feedparser's internal urllib fetch, which raised `IncompleteRead` on some MVP feeds (gzip/chunked responses). httpx reads the full body, sends a real `User-Agent`, follows redirects, and applies a 30s timeout. Floor pin (`>=0.27`) because it was already in the tree transitively via `python-telegram-bot`; resolved to `0.28.1` in `uv.lock`.
- **Note:** Wrapped behind `_http_get` and injected as the `http_get` parameter of `fetch_source(...)`, keeping the network call mockable in offline tests (same injection pattern as `parser` in `parse_content`). httpx's INFO logging is silenced in [[main]] (`logging.getLogger("httpx").setLevel(WARNING)`) because it logs the full request URL — which for the Telegram API embeds the bot token.

## Dev

### `pytest>=9`
- **Used by:** `tests/` acceptance suite and the `evals/` harness.
- **Why:** Standard Python test runner; the dev loop (stages 4–5 in `CLAUDE.md`) is TDD against pytest acceptance tests plus an LLM-judge eval harness.
- **Note:** Configured in `pyproject.toml` (`[tool.pytest.ini_options]`): `testpaths = ["tests"]`, `pythonpath = ["."]` so the `digest`/`evals` packages import without an install step (`package = false` under `[tool.uv]`).

### `ruff>=0.15`
- **Used by:** Lint + format across the repo (`uv run ruff check . && uv run ruff format .`); enforced in CI (`.github/workflows/ci.yml`).
- **Why:** Single fast Rust-based tool replacing the flake8/isort/black trio — one dependency, one config block, no per-tool version skew. Config in `pyproject.toml`: `line-length = 100`, `target-version = "py311"`, lint `select = ["E", "F", "I", "UP", "B", "SIM", "C4"]` (pycodestyle/pyflakes + import-sort + pyupgrade + bugbear + simplify + comprehensions).

## Tooling: uv + ruff (replaces pip/requirements)

As of the `chore: adopt uv + ruff` change, the project uses **uv** for environment/dependency/lock management and **ruff** for lint+format, replacing the previous flat `requirements.txt` / `requirements-dev.txt` + bare pip/venv setup.

- **Why uv over pip + requirements.txt:** reproducible installs via a committed `uv.lock` (exact transitive pins, previously absent), a single declarative `pyproject.toml` instead of split runtime/dev requirements files, and much faster CI installs (`setup-uv` + `uv sync`). The earlier "no lock manager, keep it flat" stance (see history below) was reversed because the repo is also a polygon for a clean dev loop — reproducibility and a single source of truth matter more than minimal tooling here.
- **`[tool.uv] package = false`:** the repo is an app, not a publishable library — uv manages the venv and lock without building/installing `digest` as a package. Imports resolve via pytest's `pythonpath`.
- **CI:** `.github/workflows/ci.yml` runs `ruff check` / `ruff format --check` + `pytest`; `digest.yml` switched from `setup-python` + pip install to `setup-uv` + `uv run`.

## Choices deliberately avoided

- **No `requests`:** the only direct HTTP client is `httpx` (already in the tree via python-telegram-bot), used for feed fetching; Telegram I/O stays inside python-telegram-bot. No second HTTP library.
- *(Historical)* The MVP originally avoided a lock manager and kept a flat pinned `requirements.txt`. Superseded by the uv adoption above.
- *(Historical)* The MVP originally took no direct HTTP client, fetching feeds through feedparser's built-in urllib. Superseded by the `httpx` adoption above after urllib `IncompleteRead` failures.

See [[architecture]] for where these sit in the pipeline. Open questions on dependency policy live in [[gaps]].
