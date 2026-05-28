# Architecture

Pipeline structure and deployment/scheduling topology for the digest.

Source of truth: `.github/workflows/digest.yml`, `digest/main.py`.

## Pipeline

```
[RSS/blogs] → fetch → select (dedup vs seen-state + keyword filter) → format → [Telegram]
                                      ↑
                              state/seen.json
```

Orchestrated by `digest/main.py:run` — fetch all sources (per-source failures isolated), flatten, `select` once against seen-state, then publish one message per new link. Seen-state advances per send and is saved in a `finally` so already-sent links survive a mid-run crash (no double-post, no loss). See [[modules]] (TODO) for per-module detail.

## Deployment / scheduling topology

Hosting is **GitHub Actions only** — no servers, no external scheduler. The workflow `Weekly Digest` (`.github/workflows/digest.yml`) is the entire deployment surface.

### Triggers

- **`schedule`** — cron `0 9 * * 5` = Friday 09:00 **UTC**. The weekly digest run.
- **`workflow_dispatch`** — manual trigger with a `seed_only` boolean input. When set, the run advances seen-state without posting (used once at first deploy to mark existing feed items as already-seen, so the first real run doesn't flood the channel). Maps to env `SEED_ONLY`, read by `main.py`.

### Job (`digest`, `ubuntu-latest`)

1. `actions/checkout@v4`
2. `actions/setup-python@v5` (Python 3.11)
3. `pip install -r requirements.txt`
4. **Run digest** — `python -m digest.main`, with `TELEGRAM_BOT_TOKEN` / `TELEGRAM_CHANNEL_ID` from repo **secrets** and `SEED_ONLY` from the dispatch input. The token is registered with `::add-mask::` before running.
5. **Commit updated seen-state** — commits `state/seen.json` back to the branch as `digest-bot`. No-ops if state is unchanged; otherwise `git pull --rebase` + `git push` with up to 3 retries to absorb concurrent commits.

### State as a git artifact

There is **no database**. Persistent seen-link state lives in `state/seen.json`, versioned in the repo itself and committed back by the workflow after each run. This is why the job needs `permissions: contents: write`. See [[data-model]] (TODO).

### Concurrency

`concurrency: { group: digest-state, cancel-in-progress: false }` serializes runs so a manual dispatch can't race the scheduled run while both mutate `state/seen.json`. Runs queue rather than cancel, ensuring no state write is lost.

## Notes / gaps

- Cron is UTC; Friday 09:00 UTC shifts relative to local time across DST. See [[gaps]].
- State commit-back pushes to `github.ref_name` (the branch the workflow runs on), so the workflow currently assumes it runs on the branch holding the canonical `state/seen.json`.
