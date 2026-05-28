# Wiki Changelog

Append-only log of all wiki operations. Newest at bottom.

## [2026-05-28] init

**Action:** Created wiki skeleton (index, log, gaps) during process setup. No code in repo yet.
**Pages created:** index.md, log.md, gaps.md
**Pages updated:** —
**Source:** Process setup (not codebase — repo is empty)

## [2026-05-28] mvp-implementation

**Action:** Implemented the digest MVP on branch `feat/digest-mvp` via the autopilot loop (plan -> self-review -> evals -> TDD).
**Modules created:** digest/{config,feeds,state,select,message,publish,main}.py
**Tests:** tests/ — 25 acceptance tests passing; evals/ — hybrid quality harness (format/dedup gates + optional LLM-judge relevance).
**Source:** docs/plans/2026-05-28-001-feat-digest-mvp-plan.md
**Note:** Wiki content pages (architecture, modules, data-model) not yet generated — run ~/wikis/bootstrap-wiki.md after merge to populate from the real code.

## [2026-05-28] dependencies-page

**Action:** Documented dependency rationale after a dependency change.
**Pages created:** dependencies.md
**Pages updated:** index.md (linked dependencies.md under Pages)
**Source:** requirements.txt (feedparser==6.0.11, python-telegram-bot==21.9), requirements-dev.txt (pytest==9.0.2), grounded in digest/feeds.py and digest/publish.py usage + CLAUDE.md product shape.

## [2026-05-28] architecture-page (workflow change)

**Action:** GitHub Actions workflows changed — created `architecture.md` documenting deployment/scheduling topology: trigger `0 9 * * 5` cron (Fri 09:00 UTC) + `workflow_dispatch` seed_only input; single `ubuntu-latest` job (checkout → setup-python 3.11 → pip install → run → commit seen-state back); seen-state persisted as a git artifact (`state/seen.json`, `contents: write`); `digest-state` concurrency group with `cancel-in-progress: false` to serialize runs against state races.
**Pages created:** architecture.md
**Pages updated:** index.md (linked architecture.md under Pages)
**Source:** .github/workflows/digest.yml, digest/main.py
