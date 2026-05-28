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
