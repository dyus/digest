---
date: 2026-05-28
topic: digest-mvp
---

# TG Digest — MVP Requirements

## Problem Frame

The user follows video engineering (mux/transcode/HLS/DASH/codecs) and wants to keep up with a handful of industry blogs. Browser bookmarks don't work for them — links get saved and never revisited. They read Telegram regularly. So: a private Telegram channel that receives a weekly digest of new links from curated video-engineering sources, turning "saved and forgotten" into "delivered where I already read."

Explicitly **not** wanted: AI-generated article summaries. The user wants to read the articles themselves; the digest's job is delivery and dedup, not summarization.

---

## Actors

- A1. Reader (the user): the sole consumer; reads the private channel on Telegram.
- A2. Scheduler (GitHub Actions cron): triggers the run weekly.
- A3. Digest script (Python): fetches sources, selects new items, publishes.
- A4. Telegram bot: posts messages into the private channel.

---

## Key Flows

- F1. Weekly digest run
  - **Trigger:** GitHub Actions cron (e.g. Fri 09:00).
  - **Actors:** A2, A3, A4, A1.
  - **Steps:**
    1. Script fetches each configured RSS source.
    2. Normalizes entries (title, url, published date).
    3. Loads the seen-links state; selects only items not previously published.
    4. Posts one message per new link (title + URL) to the channel via the bot.
    5. Persists the updated seen-links state.
  - **Outcome:** Channel has one new message per genuinely-new link; no repeats. If nothing new, no messages posted.
  - **Covered by:** R1, R2, R3, R4, R5, R6, R7

---

## Requirements

**Source ingestion**
- R1. Fetch entries from a configurable list of RSS/Atom sources. MVP sources: Mux Blog, Bitmovin Blog, Cloudflare Stream/Media, Demuxed / The Broadcast Knowledge.
- R2. Normalize each entry to at least: title, URL, published date. Tolerate feeds missing a published date.

**Selection (new since last run)**
- R3. Maintain persistent state of already-published link URLs across runs.
- R4. A run selects only links not already in the seen-state. Re-running with no new entries selects nothing and posts nothing.
- R5. De-duplicate within a single run (same URL appearing in multiple/again in one fetch is posted once).

**Publishing**
- R6. Post one Telegram message per selected link, containing the title and the URL, to the configured private channel. No AI-generated summary text.
- R7. After a successful run, persist the newly-published URLs into the seen-state.

**Operations**
- R8. Run unattended on a weekly GitHub Actions cron. Secrets (bot token, channel id) supplied via Actions secrets / env, never committed.

---

## Acceptance Examples

- AE1. **Covers R3, R4.** Given a seen-state already containing all current feed URLs, when a run executes, then zero messages are posted and the state is unchanged.
- AE2. **Covers R4, R6.** Given 3 feed entries of which 1 is new, when a run executes, then exactly 1 message (title + URL) is posted.
- AE3. **Covers R2.** Given a feed entry with no published date, when normalized, then the entry is still usable (not dropped, not crashing).
- AE4. **Covers R5.** Given the same URL appears twice in one fetch, when a run executes, then it is posted at most once.

---

## Success Criteria

- The reader receives a weekly message stream of genuinely new video-engineering links in their private channel, with no repeats week to week.
- A downstream implementer can build from this without inventing product behavior: selection rule, message format, sources, and state requirement are all fixed here.

---

## Scope Boundaries

- No AI-generated article summaries (deliberate — read the article, not a summary).
- No tags, read-tracking, or feedback loop in MVP (backlog).
- No public channel / multi-user — single private channel for the user.
- No web UI or dashboard — GitHub Actions + Telegram only.
- No full-text scraping — RSS/Atom metadata only.

---

## Key Decisions

- Selection = "everything new since last run": matches the weekly-digest mental model and guarantees no repeats. Requires persistent state. (vs. "recent N by date" which risks boundary repeats/misses.)
- One message per link (not a single digest post): aligns with the backlog (per-article read-tracking, feedback) and reads naturally in Telegram.
- Hosting on GitHub Actions: free, serverless, no infra to maintain.

---

## Dependencies / Assumptions

- A Telegram bot exists (or will be created) and is an admin of the private channel; token + channel id available as secrets.
- Chosen sources expose working RSS/Atom feeds (Cloudflare's feed is general and may need tag/section filtering — flagged for planning).

---

## Outstanding Questions

### Deferred to Planning

- [Affects R3, R7][Technical] Where does the seen-links state live? Commit-back file in the repo vs GitHub Actions cache vs artifact. Trade-offs (durability, race conditions, simplicity) resolved during `/plan`.
- [Affects R1][Needs research] Exact feed URLs for each source, and whether Cloudflare needs section/tag filtering to stay video-relevant.

---

## Next Steps

-> `/plan docs/brainstorms/digest-mvp-requirements.md` for structured implementation planning.
