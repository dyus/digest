# Digest Quality Rubric

The LLM-judge scores a produced digest (the list of messages a run would post) on three
dimensions, 1–5. Hard gates must pass for the run to be considered acceptable.

## Dimensions

### Relevance (gate: >= 4)
Are the posted items genuinely **video engineering** — mux, transcoding, HLS/DASH,
codecs, streaming infrastructure, playback, packaging, WebRTC, media delivery?
- 5: every item clearly on-topic for a video-engineering reader.
- 4: all on-topic; at most one borderline-but-defensible item.
- 3: a clearly off-topic item slipped through.
- 1–2: multiple off-topic items.

### Dedup (gate: == 5, deterministic)
- 5: no message URL is in the prior seen-state, and no two messages share a normalized URL.
- < 5: any repeat — automatic failure.

### Format (gate: == 5, deterministic)
- 5: every message is exactly a title line + a valid http(s) URL line, no AI summary text.
- < 5: any message missing a title, missing/!valid URL, or carrying summary cruft.

## Gates

A case PASSES only if: Format == 5 AND Dedup == 5 AND Relevance >= 4.
Format and Dedup are checked deterministically by `evals/run.py`. Relevance is scored by the
LLM judge (`evals/judge.py`) when run with `--judge`; without it, relevance is reported as
"not scored" and does not gate (so the suite is runnable with zero API cost in CI-by-default).
