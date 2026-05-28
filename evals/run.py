"""Run quality evals: build each case's digest through the real pipeline, then apply
hard gates. Format and Dedup gate always; Relevance gates only with --judge.

    python -m evals.run            # deterministic gates only (zero cost)
    python -m evals.run --judge    # also score relevance via the claude CLI
"""
import argparse
import json
import sys
from pathlib import Path

from digest.config import Source
from digest.feeds import Item
from digest.main import run
from digest.select import normalize_url

from evals import judge

CASES_DIR = Path(__file__).parent / "cases"


class _Capture:
    def __init__(self):
        self.sent = []

    def send(self, text):
        self.sent.append(text)


def _load_case(path: Path):
    data = json.loads(path.read_text())
    sources, items_by_source = [], {}
    for s in data["sources"]:
        kw = tuple(s["keywords"]) if s.get("keywords") else None
        sources.append(Source(s["name"], f"https://feed/{s['name']}", kw))
        items_by_source[s["name"]] = [
            Item(i["title"], i["url"], source=s["name"]) for i in s["items"]
        ]
    return data["name"], data.get("seen", []), sources, items_by_source


def run_case(path: Path, use_judge: bool, tmp_state: Path) -> bool:
    name, seen, sources, items_by_source = _load_case(path)
    seen_normalized = {normalize_url(u) for u in seen}
    tmp_state.write_text(json.dumps(sorted(seen_normalized)))

    pub = _Capture()
    run(sources, pub, tmp_state, lambda src: items_by_source.get(src.name, []))

    fmt, fmt_problems = judge.check_format(pub.sent)
    dedup, dedup_problems = judge.check_dedup(pub.sent, seen_normalized)

    print(f"\n[case] {name} — {len(pub.sent)} message(s)")
    print(f"  format: {fmt}/5" + (f" {fmt_problems}" if fmt_problems else ""))
    print(f"  dedup:  {dedup}/5" + (f" {dedup_problems}" if dedup_problems else ""))

    passed = fmt == 5 and dedup == 5
    if use_judge:
        rel = judge.judge_relevance(pub.sent)
        print(f"  relevance: {rel['relevance']}/5 — {rel.get('notes', '')}")
        passed = passed and rel["relevance"] >= 4
    else:
        print("  relevance: not scored (run with --judge)")
    return passed


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--judge", action="store_true", help="score relevance via claude CLI")
    args = ap.parse_args()

    import tempfile

    all_passed = True
    with tempfile.TemporaryDirectory() as d:
        tmp_state = Path(d) / "seen.json"
        for case in sorted(CASES_DIR.glob("*.json")):
            if not run_case(case, args.judge, tmp_state):
                all_passed = False

    print("\nPASS" if all_passed else "\nFAIL — a hard gate failed")
    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
