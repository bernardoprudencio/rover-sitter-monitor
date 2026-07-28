#!/usr/bin/env python3
"""Assemble the Locked Rates VoC corpus from the local dashboard exports.

Read-only over dashboard/public/data/. Emits batch/index files into an output
directory (default: the session scratchpad) that feed the parallel agent waves:

  W2 (core Reddit VoC)   -> core_batch_*.json   (rate-mgmt tagged + free-text mentions)
  W4 (supporting)        -> supporting_sample.json (adjacent pricing problems w/ signal)
  W1 (research)          -> research_index.json  (on-topic Confluence studies, if any)
  W3 (images)            -> image_candidates.json (rate posts likely to carry a screenshot)

The decision this feeds: whether to evolve Locked Rates from a binary lock/unlock
into granular per-client rate management (visibility + general edits). The corpus
is deliberately broadened past the literal "Locked rates" tag to cover rate
management for repeat/recurring clients.

Nothing here is committed data; only the script itself lives in the repo.
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = REPO_ROOT / "dashboard" / "public" / "data"

# Problem tags that put a post directly in scope (rate management for clients).
CORE_PROBLEMS = ["Locked rates", "New/repeat clients", "Flag repeat clients"]

# Free-text signals that indicate a rate-locking / rate-management post even when
# it wasn't classified under a CORE_PROBLEMS tag. Kept tight; false-friends
# (lockbox, smart lock, calendar block) are pruned via NEGATIVE_TERMS below.
LR_TERMS = [
    "locked rate", "lock rate", "lock in rate", "locked in rate", "rate locked",
    "unlock rate", "unlock the rate", "can't change rate", "cant change rate",
    "change the rate", "change their rate", "set price", "set rate",
    "repeat client rate", "returning client rate", "recurring rate",
]

# If one of these appears and no LR_TERM tag matched, the "lock"/"set" hit is
# almost certainly a false friend — drop the free-text-only candidate.
NEGATIVE_TERMS = ["lockbox", "lock box", "smart lock", "door lock", "keypad",
                  "block off", "blocked off", "block my calendar", "blocking the calendar"]

# Adjacent problems mined for the "why granular rate management" motivation.
SUPPORTING_PROBLEMS = [
    "Base rate",
    "Automated rates",
    "Pricing strategy",
    "Pricing transparency",
    "Recurring bookings",
    "Discounts / promos",
    "Holidays",
]
# A supporting post only qualifies if its text also gestures at rate control,
# repeat/recurring clients, per-client pricing, visibility, or editing rates.
MOTIVATION_TERMS = [
    "rate", "price", "pricing", "charge", "fee", "repeat client", "recurring",
    "returning client", "regular client", "lock", "unlock", "change", "edit",
    "update", "adjust", "raise", "increase", "different rate", "per client",
    "can't see", "cant see", "visibility", "holiday rate", "weekend rate",
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

    # ---- Core corpus: rate-mgmt tagged OR free-text mention ----------------
    core: dict[str, dict] = {}
    for p in posts:
        probs = p.get("problems") or []
        tagged = any(cp in probs for cp in CORE_PROBLEMS)
        blob = text_of(p, "title", "preview")
        mention = has_term(blob, LR_TERMS) and not has_term(blob, NEGATIVE_TERMS)
        if tagged or mention:
            core[p["id"]] = {
                "id": p["id"],
                "url": p.get("url"),
                "title": p.get("title") or "",
                "text": p.get("preview") or "",
                "date": p.get("date"),
                "author": p.get("author"),
                "lr_tagged": tagged,
                "free_text_only": mention and not tagged,
                "current_problems": probs,
            }
    core_list = sorted(core.values(), key=lambda r: r.get("date") or "")

    # Batches for W2 (analysis subagents ignore current_problems for scoring).
    batches = [core_list[i : i + batch_size] for i in range(0, len(core_list), batch_size)]
    for i, b in enumerate(batches):
        (out_dir / f"core_batch_{i:02d}.json").write_text(json.dumps(b, indent=2))

    # ---- Image candidates for W3: posts with little/no preview text ---------
    # Image/link posts store no selftext, so an empty preview is the best local
    # signal that the post is a screenshot (rate settings, price fields, etc.).
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
            "author": p.get("author"),
            "current_problems": probs,
        }
    supporting_list = sorted(supporting.values(), key=lambda r: r.get("date") or "")
    (out_dir / "supporting_sample.json").write_text(json.dumps(supporting_list, indent=2))

    # ---- Research index for W1 --------------------------------------------
    RESEARCH_TITLE_HINTS = [
        "locked rate", "lock rate", "rate lock", "rate management", "pricing",
        "rate", "repeat client", "recurring", "rebooking", "book again",
    ]

    def is_on_topic(r: dict) -> bool:
        if any(cp in (r.get("problems") or []) for cp in CORE_PROBLEMS):
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
        "core_lr_tagged": sum(1 for r in core_list if r["lr_tagged"]),
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
    default_out = os.environ.get("LOCKED_RATES_OUT") or str(
        Path.cwd() / "scratchpad_locked_rates"
    )
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=default_out, help="output directory for batches/indexes")
    ap.add_argument("--batch-size", type=int, default=50)
    args = ap.parse_args()
    summary = build(Path(args.out), args.batch_size)
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
