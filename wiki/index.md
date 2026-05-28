# digest — Wiki Index

*LLM-maintained knowledge base. Do not edit manually — update via the wiki protocol in CLAUDE.md.*

Status: **populated** (MVP landed on `feat/digest-mvp`). Pages are grounded in the real code under `digest/` and `evals/`.

## Pages

- [`architecture.md`](architecture.md) — pipeline structure + GitHub Actions deployment/scheduling topology
- [`modules.md`](modules.md) — one section per module in `digest/` and `evals/`
- [`data-model.md`](data-model.md) — in-memory `Item` + persistent seen-links state (`state/seen.json`)
- [`dependencies.md`](dependencies.md) — key dependency choices with rationale
- [`gaps.md`](gaps.md) — known gaps and open questions

Expected as the wiki fills in:

- `decisions.md` — lightweight ADRs from git history

## Conventions

- Pages use `[[backlinks]]` to cross-reference.
- Every page is grounded in real source or git history — never invented.
- See `log.md` for the append-only changelog.
