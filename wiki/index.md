# digest — Wiki Index

*LLM-maintained knowledge base. Do not edit manually — update via the wiki protocol in CLAUDE.md.*

Status: **skeleton** (created 2026-05-28). No code yet — pages populate as the MVP lands, via the post-commit hook and `~/wikis/bootstrap-wiki.md`.

## Pages

- [`architecture.md`](architecture.md) — pipeline structure + GitHub Actions deployment/scheduling topology
- [`dependencies.md`](dependencies.md) — key dependency choices with rationale

Expected as the MVP wiki fills in:

- `data-model.md` — persistent state (e.g. seen-links store)
- `modules/` — one page per module (sources, fetch, state, format, publish)
- `decisions.md` — lightweight ADRs from git history
- `gaps.md` — known gaps and open questions

## Conventions

- Pages use `[[backlinks]]` to cross-reference.
- Every page is grounded in real source or git history — never invented.
- See `log.md` for the append-only changelog.
