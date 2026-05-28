# Architecture

Pipeline structure and deployment/scheduling topology for the digest.

Source of truth: `.github/workflows/digest.yml`, `.github/workflows/ci.yml`, `digest/main.py`.

## Pipeline

```
[RSS/blogs] → fetch → select (dedup vs seen-state + keyword filter) → format → [Telegram]
                                      ↑
                              state/seen.json
```

Orchestrated by `digest/main.py:run` — fetch all sources (per-source failures isolated), flatten, `select` once against seen-state, then publish one message per new link. Seen-state advances per send and is saved in a `finally` so already-sent links survive a mid-run crash (no double-post, no loss). See [[modules]] (TODO) for per-module detail.

## Deployment / scheduling topology

Hosting is **GitHub Actions only** — no servers, no external scheduler. The workflow `Weekly Digest` (`.github/workflows/digest.yml`) is the entire deployment surface. A second workflow, `CI` (`.github/workflows/ci.yml`), gates code quality but does not deploy — see [[#CI workflow]] below.

### Triggers

- **`schedule`** — cron `0 9 * * 5` = Friday 09:00 **UTC**. The weekly digest run.
- **`workflow_dispatch`** — manual trigger with a `seed_only` boolean input. When set, the run advances seen-state without posting (used once at first deploy to mark existing feed items as already-seen, so the first real run doesn't flood the channel). Maps to env `SEED_ONLY`, read by `main.py`.

### Job (`digest`, `ubuntu-latest`)

1. `actions/checkout@v4`
2. `astral-sh/setup-uv@v5`
3. `uv sync --frozen` — restore the exact locked environment from `uv.lock` (fails if the lockfile is stale). See [[dependencies]].
4. **Run digest** — `uv run python -m digest.main`, with `TELEGRAM_BOT_TOKEN` / `TELEGRAM_CHANNEL_ID` from repo **secrets** and `SEED_ONLY` from the dispatch input. The token is registered with `::add-mask::` before running.
5. **Commit updated seen-state** — commits `state/seen.json` back to the branch as `digest-bot`. No-ops if state is unchanged; otherwise `git pull --rebase` + `git push` with up to 3 retries to absorb concurrent commits.

### State as a git artifact

There is **no database**. Persistent seen-link state lives in `state/seen.json`, versioned in the repo itself and committed back by the workflow after each run. This is why the job needs `permissions: contents: write`. See [[data-model]] (TODO).

### Concurrency

`concurrency: { group: digest-state, cancel-in-progress: false }` serializes runs so a manual dispatch can't race the scheduled run while both mutate `state/seen.json`. Runs queue rather than cancel, ensuring no state write is lost.

## CI workflow

The `CI` workflow (`.github/workflows/ci.yml`) is separate from deployment — it never posts or touches seen-state. It guards code quality on every change.

- **Triggers** — `push` to `main` and every `pull_request`.
- **Job (`lint-and-test`, `ubuntu-latest`)** — checkout → `astral-sh/setup-uv@v5` → `uv sync --frozen` → `uv run ruff check .` → `uv run ruff format --check .` → `uv run pytest -q`.
- Mirrors the local loop from CLAUDE.md (`ruff check`, `ruff format`, `pytest`) so a green local run matches green CI. `format --check` fails on unformatted code rather than rewriting it.

## Notes / gaps

- Cron is UTC; Friday 09:00 UTC shifts relative to local time across DST. See [[gaps]].
- State commit-back pushes to `github.ref_name` (the branch the workflow runs on), so the workflow currently assumes it runs on the branch holding the canonical `state/seen.json`.
