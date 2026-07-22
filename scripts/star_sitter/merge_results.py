#!/usr/bin/env python3
"""Merge + tally the Star Sitter VoC agent outputs into one deterministic file.

Reads every core_*.json / support_*.json the analysis subagents wrote into the
results dir, validates each row's shape, joins back to the corpus batches for
title/url/author/date, and emits:

  merged.json      -> flat list of validated rows (with source batch + record)
  tally.json       -> sentiment totals, theme_hint counts, relevance counts,
                      and per-theme top quotes (highest relevance first)

This is read-only over the scratchpad; nothing here touches the repo or sheet.
The tally feeds the headline stats + sentiment donut on the /star-sitter route,
and the per-theme quote lists seed synthesis.
"""
from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from pathlib import Path

VALID_SENTIMENT = {"positive", "negative", "mixed", "neutral"}
VALID_RELEVANCE = {"high", "medium", "low"}
VALID_THEMES = {
    "opaque-criteria", "all-or-nothing-threshold", "loss-anxiety", "weak-reward",
    "tied-to-search-and-bookings", "new-sitter-disadvantage",
    "wants-tiers-or-progression", "wants-transparency", "owner-perception",
    "praise", "other",
}


def load_corpus(corpus_dir: Path) -> dict[str, dict]:
    """Map id -> corpus record across all core/supporting inputs."""
    by_id: dict[str, dict] = {}
    for name in sorted(corpus_dir.glob("core_batch_*.json")):
        for rec in json.loads(name.read_text()):
            by_id[rec["id"]] = rec
    sup = corpus_dir / "supporting_sample.json"
    if sup.exists():
        for rec in json.loads(sup.read_text()):
            by_id[rec["id"]] = rec
    return by_id


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--corpus-dir", required=True, help="dir with core_batch_*.json etc.")
    ap.add_argument("--results-dir", required=True, help="dir with core_*.json / support_*.json")
    ap.add_argument("--out-dir", required=True)
    args = ap.parse_args()

    corpus = load_corpus(Path(args.corpus_dir))
    results_dir = Path(args.results_dir)
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    result_files = sorted(
        f for f in results_dir.glob("*.json")
        if f.name.startswith(("core_", "support_"))
    )

    merged: list[dict] = []
    problems: list[str] = []
    seen: set[str] = set()
    for f in result_files:
        try:
            rows = json.loads(f.read_text())
        except json.JSONDecodeError as e:
            problems.append(f"{f.name}: invalid JSON ({e})")
            continue
        for row in rows:
            rid = row.get("id")
            if not rid:
                problems.append(f"{f.name}: row without id")
                continue
            if row.get("sentiment") not in VALID_SENTIMENT:
                problems.append(f"{f.name}:{rid}: bad sentiment {row.get('sentiment')!r}")
            if row.get("relevance") not in VALID_RELEVANCE:
                problems.append(f"{f.name}:{rid}: bad relevance {row.get('relevance')!r}")
            hints = row.get("theme_hint") or []
            for h in hints:
                if h not in VALID_THEMES:
                    problems.append(f"{f.name}:{rid}: unknown theme_hint {h!r}")
            src = corpus.get(rid, {})
            if rid in seen:
                continue  # a post could appear in both core and supporting; keep first
            seen.add(rid)
            merged.append({
                **row,
                "source_file": f.name,
                "title": src.get("title", ""),
                "url": row.get("url") or src.get("url"),
                "author": src.get("author"),
                "corpus_date": src.get("date"),
                "ss_tagged": src.get("ss_tagged"),
                "current_problems": src.get("current_problems", []),
            })

    # ---- Tallies -----------------------------------------------------------
    sentiment = Counter(r["sentiment"] for r in merged if r.get("sentiment") in VALID_SENTIMENT)
    relevance = Counter(r["relevance"] for r in merged if r.get("relevance") in VALID_RELEVANCE)
    theme_counts: Counter = Counter()
    theme_sentiment: dict[str, Counter] = defaultdict(Counter)
    theme_quotes: dict[str, list[dict]] = defaultdict(list)
    rel_rank = {"high": 0, "medium": 1, "low": 2}
    for r in merged:
        for h in (r.get("theme_hint") or []):
            if h not in VALID_THEMES:
                continue
            theme_counts[h] += 1
            if r.get("sentiment") in VALID_SENTIMENT:
                theme_sentiment[h][r["sentiment"]] += 1
            if r.get("quote"):
                theme_quotes[h].append({
                    "text": r["quote"],
                    "url": r.get("url"),
                    "date": r.get("corpus_date") or r.get("date"),
                    "author": r.get("author"),
                    "relevance": r.get("relevance"),
                    "sentiment": r.get("sentiment"),
                    "signal": r.get("signal"),
                })
    for h in theme_quotes:
        theme_quotes[h].sort(key=lambda q: rel_rank.get(q.get("relevance"), 3))

    tally = {
        "total_rows": len(merged),
        "unique_posts": len(seen),
        "result_files": [f.name for f in result_files],
        "sentiment": dict(sentiment),
        "relevance": dict(relevance),
        "theme_counts": dict(theme_counts.most_common()),
        "theme_sentiment": {h: dict(c) for h, c in theme_sentiment.items()},
        "theme_quotes": theme_quotes,
        "validation_problems": problems,
    }

    (out_dir / "merged.json").write_text(json.dumps(merged, indent=2))
    (out_dir / "tally.json").write_text(json.dumps(tally, indent=2))

    print(json.dumps({
        "merged_rows": len(merged),
        "unique_posts": len(seen),
        "result_files": len(result_files),
        "sentiment": dict(sentiment),
        "relevance": dict(relevance),
        "theme_counts": dict(theme_counts.most_common()),
        "validation_problems": len(problems),
    }, indent=2))


if __name__ == "__main__":
    main()
