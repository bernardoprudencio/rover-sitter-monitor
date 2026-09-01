#!/usr/bin/env python3
"""Assemble the Inbox & Chat VoC corpus from the dashboard exports.

Read-only over the dashboard data dir. Emits batch/index files into an output
directory (default: ./scratchpad_inbox_chat) that feed the parallel agent waves:

  W2 (core Reddit VoC)   -> core_batch_*.json   (Communication-tagged + free-text)
  W4 (supporting)        -> supporting_sample.json (adjacent surfaces w/ signal)
  W1 (research)          -> research_index.json  (on-topic Confluence studies)
  W3 (images)            -> image_candidates.json (posts likely to carry a screenshot)

The question this feeds is exploratory, not a yes/no bet: *where does messaging
hurt most for sitters and owners, and what should we fix first?* Scope is the
four core surfaces (inbox list, message thread, media in messages, message
notifications) plus four adjacent ones (off-platform/contact-info blocking,
Rover Support inside threads, Rover Cards photos, booking-request messaging).

Two things differ from scripts/locked_rates/ and scripts/star_sitter/:

  1. `--data-dir` is a flag, not a module constant. `make export` needs sheet
     credentials that aren't present on every machine; the live export is also
     downloadable from the Pages deploy. Either way the builder reads the same
     four files.
  2. The adjacent ring is capped per problem. `Difficult clients` (2,911 posts),
     `Rover Support quality` (561) and `Going off app` (513) are large enough to
     swamp a messaging corpus, so the ring is gated AND capped, and the summary
     reports pre- and post-cap counts so the truncation is never silent.

Nothing here is committed data; only the script itself lives in the repo.
"""
from __future__ import annotations

import argparse
import json
import os
import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_DATA_DIR = REPO_ROOT / "dashboard" / "public" / "data"

# ---------------------------------------------------------------------------
# Ring 1 — core. The `Communication` theme minus `Flag repeat clients`.
#
# `Flag repeat clients` is excluded deliberately: despite sitting under
# Communication it is a clients/rates problem, it is the single largest tag in
# the theme (137 of 560), and it was already a CORE_PROBLEMS tag for the Locked
# Rates report. Including it here would double-count across reports and pull
# rate-negotiation noise into a messaging corpus. It lives in the ring below.
# ---------------------------------------------------------------------------
CORE_PROBLEMS = [
    "Media uploads",
    "Functionality",
    "Archiving conversations",
    "Video calls",
    "Reminders",
    "Custom/saved responses",
    "Auto-correct",
]

# Free-text signals carry most of the recall for this topic: taxonomy.json has
# no bare `message`, `messaging`, `inbox`, `chat`, `dm`, `notification` or
# `photo` keyword anywhere, so the tag-based corpus badly under-collects.
# Grouped by surface so coverage stays auditable.
IC_TERMS = [
    # --- inbox list & organization ---
    "inbox", "my messages", "message list", "conversation list", "archive",
    "unread", "filter conversations", "search messages", "search my inbox",
    "find the conversation", "old conversation",
    # --- message thread & composing ---
    "message thread", "conversation screen", "send a message",
    "message wouldn't send", "message didn't send", "message failed",
    "can't message", "cant message", "message disappeared", "deleted message",
    "unsend", "read receipt", "message order", "double message",
    "duplicate conversation",
    # --- media in messages ---
    "send photo", "send a picture", "send picture", "send video",
    "upload photo", "upload video", "upload failed", "photo won't upload",
    "photo wont upload", "video won't upload", "attach photo",
    "picture quality", "photo quality", "blurry", "compressed",
    "file too large", "video too long",
    # --- message notifications ---
    "notification", "push notification", "didn't get notified",
    "no notification", "missed message", "text alert", "sms",
]

# If one of these appears and no CORE_PROBLEMS tag matched, the hit is almost
# certainly a false friend — drop the free-text-only candidate.
NEGATIVE_TERMS = [
    "live chat", "chat with support", "support chat", "chatgpt",
    "profile photo", "profile picture", "listing photo", "photo of my house",
    "attached to", "rover card", "archive the listing", "archived listing",
]

# ---------------------------------------------------------------------------
# Ring 2 — adjacent surfaces, gated and capped.
# ---------------------------------------------------------------------------
SUPPORTING_PROBLEMS = [
    # off-platform / contact-info blocking
    "Going off app", "Off-platform management",
    # Rover Support inside threads
    "Rover Support quality",
    # Rover Cards / report-card photos
    "Sending videos", "Live updates", "Glitches and bugs (Cards)",
    # booking-request messaging
    "Intake form", "CMS", "Customize request",
    # general surfaces that often carry messaging complaints
    "Difficult clients", "Glitches / lag / bugs", "Navigation",
    "Web / app parity", "Flag repeat clients",
]

# A supporting post only qualifies if its text also gestures at messaging.
MOTIVATION_TERMS = [
    "message", "messages", "messaging", "inbox", "chat", "conversation",
    "thread", "reply", "respond", "response time", "response rate",
    "notification", "photo", "picture", "video", "upload",
    "unread", "phone number", "text me", "texted", "blocked", "flagged",
    "censored",
]

# No single large problem may dominate the adjacent ring.
SUPPORTING_CAP_PER_PROBLEM = 60

RESEARCH_TITLE_HINTS = [
    "inbox", "message", "messaging", "chat", "conversation", "photo", "media",
    "upload", "notification", "communication", "thread",
]


def load_current(data_dir: Path, kind: str) -> list[dict]:
    meta = json.loads((data_dir / "meta.json").read_text())
    key = {"posts": "posts_file", "research": "research_file"}[kind]
    fname = meta.get(key)
    if not fname:
        return []
    return json.loads((data_dir / fname).read_text())


def text_of(rec: dict, *fields: str) -> str:
    return " ".join((rec.get(f) or "") for f in fields).lower()


# Bare substring matching produces false hits that are easy to miss: "sms"
# matches "mannerisms" and "criticisms", "typing" matches "prototyping". Match
# on word boundaries instead, with a tolerant suffix group so one listed term
# still covers its plural/past/gerund forms ("archive" -> archives, archived,
# archiving; "notification" -> notifications; "upload photo" -> upload photos).
_TERM_CACHE: dict[str, "re.Pattern[str]"] = {}


def _pattern(term: str) -> "re.Pattern[str]":
    pat = _TERM_CACHE.get(term)
    if pat is None:
        pat = re.compile(r"\b" + re.escape(term) + r"(?:s|es|ed|ing)?\b")
        _TERM_CACHE[term] = pat
    return pat


def has_term(blob: str, terms: list[str]) -> bool:
    return any(_pattern(t).search(blob) for t in terms)


def matched_terms(blob: str, terms: list[str]) -> list[str]:
    """Which terms fired — used by the contamination audit, not the build."""
    return [t for t in terms if _pattern(t).search(blob)]


def build(data_dir: Path, out_dir: Path, batch_size: int) -> dict:
    out_dir.mkdir(parents=True, exist_ok=True)
    posts = load_current(data_dir, "posts")
    research = load_current(data_dir, "research")

    # ---- Core corpus: Communication-tagged OR free-text mention -----------
    core: dict[str, dict] = {}
    for p in posts:
        probs = p.get("problems") or []
        tagged = any(cp in probs for cp in CORE_PROBLEMS)
        blob = text_of(p, "title", "preview")
        mention = has_term(blob, IC_TERMS) and not has_term(blob, NEGATIVE_TERMS)
        if tagged or mention:
            core[p["id"]] = {
                "id": p["id"],
                "url": p.get("url"),
                "title": p.get("title") or "",
                "text": p.get("preview") or "",
                "date": p.get("date"),
                "author": p.get("author"),
                "ic_tagged": tagged,
                "free_text_only": mention and not tagged,
                "current_problems": probs,
            }
    core_list = sorted(core.values(), key=lambda r: r.get("date") or "")

    batches = [core_list[i : i + batch_size] for i in range(0, len(core_list), batch_size)]
    for i, b in enumerate(batches):
        (out_dir / f"core_batch_{i:02d}.json").write_text(json.dumps(b, indent=2))

    # ---- Image candidates for W3: posts with little/no preview text --------
    image_candidates = [
        {"id": r["id"], "url": r["url"], "title": r["title"], "date": r["date"]}
        for r in core_list
        if len((r["text"] or "").strip()) < 15
    ]
    (out_dir / "image_candidates.json").write_text(json.dumps(image_candidates, indent=2))

    # ---- Supporting ring for W4: gated, then capped per problem ------------
    pre_cap: dict[str, list[dict]] = {sp: [] for sp in SUPPORTING_PROBLEMS}
    for p in posts:
        if p["id"] in core:
            continue
        probs = p.get("problems") or []
        hits = [sp for sp in SUPPORTING_PROBLEMS if sp in probs]
        if not hits:
            continue
        blob = text_of(p, "title", "preview")
        if not has_term(blob, MOTIVATION_TERMS):
            continue
        if has_term(blob, NEGATIVE_TERMS):
            continue
        rec = {
            "id": p["id"],
            "url": p.get("url"),
            "title": p.get("title") or "",
            "text": p.get("preview") or "",
            "date": p.get("date"),
            "author": p.get("author"),
            "current_problems": probs,
            "supporting_for": hits,
        }
        for sp in hits:
            pre_cap[sp].append(rec)

    # Newest-first within each problem, cap, then merge and dedupe by id.
    supporting: dict[str, dict] = {}
    cap_report: dict[str, dict] = {}
    for sp, recs in pre_cap.items():
        recs.sort(key=lambda r: r.get("date") or "", reverse=True)
        kept = recs[:SUPPORTING_CAP_PER_PROBLEM]
        cap_report[sp] = {"pre_cap": len(recs), "post_cap": len(kept),
                          "dropped": max(0, len(recs) - len(kept))}
        for r in kept:
            supporting.setdefault(r["id"], r)
    supporting_list = sorted(supporting.values(), key=lambda r: r.get("date") or "")
    (out_dir / "supporting_sample.json").write_text(json.dumps(supporting_list, indent=2))

    sup_batches = [
        supporting_list[i : i + batch_size]
        for i in range(0, len(supporting_list), batch_size)
    ]
    for i, b in enumerate(sup_batches):
        (out_dir / f"support_batch_{i:02d}.json").write_text(json.dumps(b, indent=2))

    # ---- Research index for W1 --------------------------------------------
    # Only 78 of ~1,554 Confluence rows survive the dashboard eligibility
    # filter, and this topic is rich in shapes that filter drops (scripts,
    # pre-cursor studies). This index is the local floor; the research wave
    # also runs a live CQL sweep and reconciles by page id.
    def is_on_topic(r: dict) -> bool:
        if any(cp in (r.get("problems") or []) for cp in CORE_PROBLEMS):
            return True
        return has_term(text_of(r, "title", "excerpt"), RESEARCH_TITLE_HINTS)

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
        "data_dir": str(data_dir),
        "out_dir": str(out_dir),
        "total_posts": len(posts),
        "core_posts": len(core_list),
        "core_ic_tagged": sum(1 for r in core_list if r["ic_tagged"]),
        "core_free_text_only": sum(1 for r in core_list if r["free_text_only"]),
        "core_batches": len(batches),
        "batch_size": batch_size,
        "image_candidates": len(image_candidates),
        "supporting_unique": len(supporting_list),
        "supporting_batches": len(sup_batches),
        "supporting_cap_per_problem": SUPPORTING_CAP_PER_PROBLEM,
        "supporting_cap_report": cap_report,
        "supporting_dropped_total": sum(v["dropped"] for v in cap_report.values()),
        "research_studies": len(research_index),
    }
    (out_dir / "corpus_summary.json").write_text(json.dumps(summary, indent=2))
    return summary


def main() -> None:
    default_out = os.environ.get("INBOX_CHAT_OUT") or str(
        Path.cwd() / "scratchpad_inbox_chat"
    )
    ap = argparse.ArgumentParser()
    ap.add_argument("--data-dir", default=str(DEFAULT_DATA_DIR),
                    help="dir holding meta.json + the hashed export files")
    ap.add_argument("--out", default=default_out, help="output dir for batches/indexes")
    ap.add_argument("--batch-size", type=int, default=60)
    args = ap.parse_args()
    summary = build(Path(args.data_dir), Path(args.out), args.batch_size)
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
