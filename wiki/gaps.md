# Gaps & Open Questions

Things the wiki does not yet cover, or open questions about the codebase.

## Current

- MVP code exists on `feat/digest-mvp` but wiki content pages are not yet generated. Run `~/wikis/bootstrap-wiki.md` after merge to populate the wiki from real source.
- **Feed liveness (verified 2026-05-28):** Mux (`rss.xml`, 15 items) and Cloudflare (`/rss/`, 20 items, keyword-filtered to video topics) fetch fine via the httpx fetcher. **Bitmovin** (`/blog/feed/`) and **The Broadcast Knowledge** (`/feed/`) time out (ReadTimeout) — but this was from a sandboxed network that likely blocks those hosts; not confirmed dead. Re-verify from a normal network / GitHub Actions; if they still time out, find alternate feed URLs or drop them (the run already skips failing sources gracefully). Demuxed was not included pending a usable article RSS.

## Deferred to planning

- Seen-links state storage mechanism (commit-back file vs Actions cache vs artifact) — decided during `/plan`.
