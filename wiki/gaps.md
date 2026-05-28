# Gaps & Open Questions

Things the wiki does not yet cover, or open questions about the codebase.

## Current

- MVP code exists on `feat/digest-mvp` but wiki content pages are not yet generated. Run `~/wikis/bootstrap-wiki.md` after merge to populate the wiki from real source.
- **Feed URLs not live-verified.** Candidate URLs in `digest/config.py` (Mux, Bitmovin, Cloudflare, The Broadcast Knowledge) have not been fetched against the live web yet — verify each parses before/at first deploy. Demuxed was not included pending confirmation it exposes a usable article RSS.

## Deferred to planning

- Seen-links state storage mechanism (commit-back file vs Actions cache vs artifact) — decided during `/plan`.
