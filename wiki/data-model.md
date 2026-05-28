# Data Model

## Item (in-memory)

`digest/feeds.py:Item` — a frozen dataclass: `title`, `url`, `published` (optional), `source` (optional). Built by `normalize(entry, source)` from a feedparser entry; `published` falls back `published → updated → None`. Items are never persisted — they exist only for the duration of a run.

## Seen-links state (`state/seen.json`)

The only persistent state. A JSON **array of normalized URL strings** representing links already published. Managed by `digest/state.py`:

- `load(path) → set[str]` — returns `set()` if the file is absent (first run).
- `save(path, urls)` — writes **sorted** JSON (stable, reviewable diffs), filtering out invalid URLs so they never persist. Creates parent dirs.

### Stored form is the dedup key, not the raw URL

URLs are stored after `normalize_url` ([[modules#select]]): tracking params stripped (`utm_*`, `fbclid`, `gclid`, `ref`, `mc_cid`), trailing slash and fragment removed. This is the dedup key — comparing normalized keys means the same article via different tracking links is posted once. The harness biases to **under-collapse** (only known tracking params stripped) to avoid silently dropping distinct articles.

### Validity rules (`state.is_valid_url`)

Only `http`/`https`, non-empty netloc, no userinfo (`@` in netloc rejected — keeps credentials out of committed history), length ≤ 2048. Invalid URLs are dropped at `save` time.

### Persistence semantics

- State advances **per send** inside `run`, and is written in a `finally` block — a mid-run crash keeps already-sent links (no double-post on retry, no loss). See [[architecture]].
- The file is **versioned in the repo** and committed back by the GitHub Actions workflow after each run (`permissions: contents: write`). No database. This resolves the state-storage question deferred during planning.
- `STATE_PATH` env overrides the default `state/seen.json`.
