# Modules

One section per module in `digest/` (plus `evals/`). All network and Telegram I/O is behind injectable seams, so the core is pure and testable. See [[architecture]] for how they compose and [[data-model]] for persistent state.

## config

`digest/config.py` — declarative source list. `Source` is a frozen dataclass: `name`, `feed_url`, optional `keywords`. `SOURCES` lists Mux, Bitmovin, Cloudflare, The Broadcast Knowledge. Cloudflare's feed is general-purpose, so it carries `CLOUDFLARE_KEYWORDS` (stream, video, codec, hls, dash, transcode, encode, webrtc, media) to keep only video-engineering posts. Feed URLs are not yet live-verified — see [[gaps]].

## feeds

`digest/feeds.py` — fetch + parse. `Item` model (see [[data-model]]). `normalize(entry, source)` maps a feedparser entry to an `Item`. `parse_content(content, source)` is pure (no network) — parses already-retrieved bytes/str, used by tests with fixtures. `fetch_source(source, parser=feedparser.parse)` is the network seam; `parser` is injectable. May raise on DNS/timeout/HTTP — `main.run` isolates per-source failures.

## state

`digest/state.py` — load/save the seen-links set + URL validation. Fully covered in [[data-model]].

## select

`digest/select.py` — the dedup + filter core. `normalize_url(url)` produces the dedup key (strips known tracking params, trailing slash, fragment; biased to under-collapse). `select(items, seen, keywords_by_source)` returns new, deduped (incl. cross-source via an in-run seen set), keyword-filtered items **in input order**. Keyword match is case-insensitive against the title; no keywords = pass-through.

## message

`digest/message.py` — `format_item(item)` renders one plain-text message: `title\nurl`, or just the URL if title is empty. No AI summaries (product decision: reader wants the articles themselves).

## publish

`digest/publish.py` — `Publisher` Protocol + `TelegramPublisher`, a synchronous facade over async python-telegram-bot v20+. Sends `parse_mode=None` (feed titles are untrusted third-party content — never interpreted as Telegram markup). On `RetryAfter` it sleeps and retries; other errors are logged as **type + status only** (never the raw message/URL, which embeds the bot token) and re-raised. `send_delay` (default 3s) throttles between sends.

## main

`digest/main.py` — `run(...)` orchestrator and `main()` env entrypoint. Full flow in [[architecture]]. Returns `{"selected", "sent", "seeded"}`.

## evals

`evals/` — quality harness, separate from `tests/`. `judge.py`: `check_format` (each message must be exactly `title\nurl`) and `check_dedup` (no already-seen, no in-run duplicates) are deterministic 5-or-1 gates; `judge_relevance` shells out to the local `claude` CLI against `rubric.md` for a 1–5 video-engineering relevance score. `run.py` loads JSON cases from `evals/cases/`, drives each through the **real** `digest.main.run` with a capturing publisher, and applies gates. Format+dedup must be 5/5; with `--judge`, relevance must be ≥4. Runs at zero cost unless `--judge` is passed.
