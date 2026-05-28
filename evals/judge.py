"""Quality judging for produced digests.

Deterministic checks (format, dedup) need no LLM. Relevance is scored by an LLM judge
via the local `claude` CLI when available; callers may skip it to run at zero cost.
"""

import json
import re
import shutil
import subprocess
from pathlib import Path

from digest.select import normalize_url

_URL_RE = re.compile(r"^https?://[^\s]+$")
_RUBRIC = (Path(__file__).parent / "rubric.md").read_text()


def check_format(messages: list[str]) -> tuple[int, list[str]]:
    problems = []
    for m in messages:
        lines = m.split("\n")
        if len(lines) != 2 or not lines[0].strip() or not _URL_RE.match(lines[1].strip()):
            problems.append(f"bad format: {m!r}")
    return (5 if not problems else 1), problems


def check_dedup(messages: list[str], seen_normalized: set[str]) -> tuple[int, list[str]]:
    problems = []
    keys = []
    for m in messages:
        url = m.split("\n")[-1].strip()
        key = normalize_url(url)
        if key in seen_normalized:
            problems.append(f"already seen: {url}")
        if key in keys:
            problems.append(f"duplicate in run: {url}")
        keys.append(key)
    return (5 if not problems else 1), problems


def judge_relevance(messages: list[str]) -> dict:
    """Score video-engineering relevance via the local `claude` CLI. Returns
    {"relevance": int, "notes": str}. Raises if no judge backend is available.
    """
    claude = shutil.which("claude")
    if not claude:
        raise RuntimeError("no `claude` CLI available to judge relevance")
    prompt = (
        f"{_RUBRIC}\n\nScore ONLY the Relevance dimension for these digest messages.\n"
        f'Return strict JSON: {{"relevance": <1-5>, "notes": "<short>"}}.\n\n'
        + "\n---\n".join(messages)
    )
    out = subprocess.run(
        [claude, "-p", prompt, "--max-budget-usd", "0.20"],
        capture_output=True,
        text=True,
        timeout=120,
    ).stdout
    match = re.search(r"\{.*\}", out, re.DOTALL)
    if not match:
        raise RuntimeError(f"could not parse judge output: {out[:200]!r}")
    return json.loads(match.group(0))
