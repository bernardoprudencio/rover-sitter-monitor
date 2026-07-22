#!/usr/bin/env python3
"""Assemble the Star Sitter VoC corpus from the local dashboard exports.

Read-only over dashboard/public/data/. Emits batch/index files into an output
directory (default: the session scratchpad) that feed the parallel agent waves
described in the plan:

  W2 (core Reddit VoC)   -> core_batch_*.json   (SS-tagged + free-text mentions)
  W4 (supporting)        -> supporting_sample.json (adjacent problems w/ SS/tier signal)
  W1 (research)          -> research_index.json  (the on-topic Confluence studies)
  W3 (images)            -> image_candidates.json (SS posts likely to carry a screenshot)

Nothing here is committed data; only the script itself lives in the repo.
"""
from __future__ import annotations

import argparse
import json
import os
import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = REPO_ROOT / "dashboard" / "public" / "data"

# Free-text signals that indicate a Star Sitter mention even when the post
# wasn't classified under the "Star Sitter" problem.
SS_TERMS = ["star sitter", "top sitter", "sitter badge", "elite sitter"]

# Adjacent problems mined for the "why move to tiers" motivation.
SUPPORTING_PROBLEMS = [
    "Search rank",
    "Low demand",
    "Star ratings and reviews",
    "Self promotion",
    "Insights",
    "Pricing strategy",
]
# A supporting post only qualifies if its text also gestures at status /
# recognition / progression / earnings tied to standing.
MOTIVATION_TERMS = [
    "star sitter", "top sitter", "sitter badge", "badge", "tier", "loyalty",
    "reward", "recognition", "rank", "ranking", "visibility", "promoted",
    "algorithm", "search results", "more bookings", "no bookings", "slow",
]

# On-topic Confluence studies (title match, DSN/PSD). Verified from the local
# research export; W1 fans one agent per entry.
RESEARCH_TITLE_HINTS = [
    "star sitter",
    "sitter rewards",
    "sitter performance score",
    "top 20%",
    "top 20 %",
]


def load_current(kind: str) -> list[dict]:
    meta = json.loads((DATA_DIR / "meta.json").read_text())
    key = {"posts": "posts_file", "research": "research_file"}[kind]
    fname = meta.get(key)
    if not fname:
        return []
    return json.loads((DATA_DIR / fname).read_text())


def text_of(rec: dict, *fields: str) -> str:
    return " ".join((rec.get(f) or "") for f in fields).lower()


def has_term(blob: str, terms: list[str]) -> bool:
    return any(t in blob for t in terms)


def build(out_dir: Path, batch_size: int) -> dict:
    out_dir.mkdir(parents=True, exist_ok=True)
    posts = load_current("posts")
    research = load_current("research")

    # ---- Core corpus: SS-tagged OR free-text mention -----------------------
    core: dict[str, dict] = {}
    for p in posts:
        tagged = "Star Sitter" in (p.get("problems") or [])
        blob = text_of(p, "title", "preview")
        mention = has_term(blob, SS_TERMS)
        if tagged or mention:
            core[p["id"]] = {
                "id": p["id"],
                "url": p.get("url"),
                "title": p.get("title") or "",
                "text": p.get("preview") or "",
                "date": p.get("date"),
                "author": p.get("author"),
                "ss_tagged": tagged,
                "free_text_only": mention and not tagged,
                "current_problems": p.get("problems") or [],
            }
    core_list = sorted(core.values(), key=lambda r: r.get("date") or "")

    # Batches for W2 (analysis subagents ignore current_problems for scoring).
    batches = [core_list[i : i + batch_size] for i in range(0, len(core_list), batch_size)]
    for i, b in enumerate(batches):
        (out_dir / f"core_batch_{i:02d}.json").write_text(json.dumps(b, indent=2))

    # ---- Image candidates for W3: SS posts with little/no preview text ------
    # Image/link posts store no selftext, so an empty preview is the best local
    # signal that the post is a screenshot (stats, criteria, badge, etc.).
    image_candidates = [
        {"id": r["id"], "url": r["url"], "title": r["title"], "date": r["date"]}
        for r in core_list
        if len((r["text"] or "").strip()) < 15
    ]
    (out_dir / "image_candidates.json").write_text(json.dumps(image_candidates, indent=2))

    # ---- Supporting sample for W4 ------------------------------------------
    supporting: dict[str, dict] = {}
    for p in posts:
        if p["id"] in core:
            continue
        probs = p.get("problems") or []
        if not any(sp in probs for sp in SUPPORTING_PROBLEMS):
            continue
        blob = text_of(p, "title", "preview")
        if not has_term(blob, MOTIVATION_TERMS):
            continue
        supporting[p["id"]] = {
            "id": p["id"],
            "url": p.get("url"),
            "title": p.get("title") or "",
            "text": p.get("preview") or "",
            "date": p.get("date"),
            "current_problems": probs,
        }
    supporting_list = sorted(supporting.values(), key=lambda r: r.get("date") or "")
    (out_dir / "supporting_sample.json").write_text(json.dumps(supporting_list, indent=2))

    # ---- Research index for W1 --------------------------------------------
    def is_on_topic(r: dict) -> bool:
        if "Star Sitter" in (r.get("problems") or []):
            return True
        blob = text_of(r, "title", "excerpt")
        return has_term(blob, RESEARCH_TITLE_HINTS)

    research_index = [
        {
            "id": r.get("id"),
            "space": r.get("space"),
            "title": r.get("title"),
            "url": r.get("url"),
            "author": r.get("author"),
            "updated": r.get("updated"),
            "excerpt": r.get("excerpt"),
            "problems": r.get("problems"),
        }
        for r in research
        if is_on_topic(r)
    ]
    (out_dir / "research_index.json").write_text(json.dumps(research_index, indent=2))

    summary = {
        "out_dir": str(out_dir),
        "total_posts": len(posts),
        "core_posts": len(core_list),
        "core_ss_tagged": sum(1 for r in core_list if r["ss_tagged"]),
        "core_free_text_only": sum(1 for r in core_list if r["free_text_only"]),
        "core_batches": len(batches),
        "batch_size": batch_size,
        "image_candidates": len(image_candidates),
        "supporting_sample": len(supporting_list),
        "research_studies": len(research_index),
    }
    (out_dir / "corpus_summary.json").write_text(json.dumps(summary, indent=2))
    return summary


def main() -> None:
    default_out = os.environ.get("STAR_SITTER_OUT") or str(
        Path.cwd() / "scratchpad_star_sitter"
    )
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=default_out, help="output directory for batches/indexes")
    ap.add_argument("--batch-size", type=int, default=50)
    args = ap.parse_args()
    summary = build(Path(args.out), args.batch_size)
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
