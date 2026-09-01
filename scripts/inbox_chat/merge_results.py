#!/usr/bin/env python3
"""Merge + tally the Inbox & Chat VoC agent outputs into one deterministic file.

Reads every core_*.json / support_*.json the analysis subagents wrote into the
results dir, validates each row's shape, joins back to the corpus batches for
title/url/author/date, and emits:

  merged.json      -> flat list of validated rows (with source batch + record)
  tally.json       -> sentiment totals, theme_hint counts, relevance counts,
                      and per-theme top quotes (highest relevance first)

This is read-only over the scratchpad; nothing here touches the repo or sheet.
The tally feeds the headline stats + sentiment donut on the /inbox-chat route,
and the per-theme quote lists seed synthesis. `VALID_THEMES` below MUST stay
byte-identical to the theme_hint list in analysis_prompt.md.
"""
from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from pathlib import Path

VALID_SENTIMENT = {"positive", "negative", "mixed", "neutral"}
VALID_RELEVANCE = {"high", "medium", "low"}
VALID_THEMES = {
    "inbox-hard-to-navigate", "inbox-search-missing",
    "archive-unread-confusion", "thread-tied-to-booking",
    "message-send-failure", "message-missing-or-lost",
    "media-upload-failure", "media-quality-or-limits",
    "notification-missed", "notification-noise",
    "contact-info-blocked", "support-in-thread",
    "cards-photo-issues", "request-message-pressure",
    "praise", "other",
}


def norm(s: str) -> str:
    """Fold smart punctuation and collapse whitespace before comparing.

    Reddit bodies use curly quotes and em-dashes; model output routinely
    substitutes the ASCII forms. Without this fold, a genuinely verbatim quote
    fails the substring check on punctuation alone.
    """
    s = (s or "").lower()
    for a, b in (
        ("\u2019", "'"), ("\u2018", "'"), ("\u201c", '"'), ("\u201d", '"'),
        ("\u2014", "-"), ("\u2013", "-"), ("\u00a0", " "), ("\u2026", "..."),
    ):
        s = s.replace(a, b)
    return " ".join(s.split())


def verify_quote(quote: str, record: dict) -> bool:
    """True when `quote` is a verbatim span of the record's title + preview.

    Neither scripts/star_sitter/ nor scripts/locked_rates/ actually performed
    this check, even though both content modules claim every quote was
    "machine-verified as a verbatim substring of its source post". It matters
    more here: ~51% of previews in this corpus sit at the 500-char PREVIEW_MAX
    boundary, so a model can easily complete a sentence that the source cuts
    off. Only quotes returning True should be shipped in the content module.
    """
    if not quote:
        return False
    haystack = norm(f"{record.get('title', '')} {record.get('text', '')}")
    return norm(quote) in haystack


def load_corpus(corpus_dir: Path) -> dict[str, dict]:
    """Map id -> corpus record across all core/supporting inputs."""
    by_id: dict[str, dict] = {}
    for name in sorted(corpus_dir.glob("core_batch_*.json")):
        for rec in json.loads(name.read_text()):
            by_id[rec["id"]] = rec
    for name in sorted(corpus_dir.glob("support_batch_*.json")):
        for rec in json.loads(name.read_text()):
            by_id[rec["id"]] = rec
    sup = corpus_dir / "supporting_sample.json"
    if sup.exists():
        for rec in json.loads(sup.read_text()):
            by_id.setdefault(rec["id"], rec)
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
    unverified: list[dict] = []
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
            row_quote_ok = verify_quote(row.get("quote", ""), src)
            if row.get("quote") and not row_quote_ok:
                unverified.append({"id": rid, "quote": row.get("quote"),
                                   "source_file": f.name})
            merged.append({
                **row,
                "quote_verified": row_quote_ok,
                "source_file": f.name,
                "title": src.get("title", ""),
                "url": row.get("url") or src.get("url"),
                "author": src.get("author"),
                "corpus_date": src.get("date"),
                "ic_tagged": src.get("ic_tagged"),
                "current_problems": src.get("current_problems", []),
            })

    # ---- Content dedupe ----------------------------------------------------
    # The id dedupe above only catches the same POST arriving twice (core +
    # supporting). It does not catch the same CONTENT posted twice: this
    # subreddit carries re-posts and title/body variants from one author within
    # the same minute, which the export gives distinct ids (id = sha1(url)).
    # Measured at ~4% of the core corpus. Left in, they inflate every theme
    # count and can put the same quote on the page twice, so collapse them on
    # (normalized title, author, date) and keep the richest variant.
    by_content: dict[tuple, dict] = {}
    content_dupes = 0
    for r in merged:
        ckey = (
            " ".join((r.get("title") or "").lower().split()),
            r.get("author"),
            r.get("corpus_date"),
        )
        if not ckey[0]:
            by_content[(r["id"],)] = r  # no title to compare on; keep as-is
            continue
        prev = by_content.get(ckey)
        if prev is None:
            by_content[ckey] = r
        else:
            content_dupes += 1
            # Prefer the variant the model could actually read, then the one
            # with a verified quote.
            better = max(
                (prev, r),
                key=lambda x: (bool(x.get("text_available")), bool(x.get("quote_verified"))),
            )
            by_content[ckey] = better
    merged = list(by_content.values())

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
            if r.get("quote") and r.get("quote_verified"):
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
        "content_duplicates_collapsed": content_dupes,
        "result_files": [f.name for f in result_files],
        "sentiment": dict(sentiment),
        "relevance": dict(relevance),
        "theme_counts": dict(theme_counts.most_common()),
        "theme_sentiment": {h: dict(c) for h, c in theme_sentiment.items()},
        "theme_quotes": theme_quotes,
        "quotes_offered": sum(1 for r in merged if r.get("quote")),
        "quotes_verified": sum(1 for r in merged if r.get("quote_verified")),
        "quotes_unverified": unverified,
        "validation_problems": problems,
    }

    (out_dir / "merged.json").write_text(json.dumps(merged, indent=2))
    (out_dir / "tally.json").write_text(json.dumps(tally, indent=2))

    print(json.dumps({
        "merged_rows": len(merged),
        "unique_posts": len(seen),
        "content_duplicates_collapsed": content_dupes,
        "result_files": len(result_files),
        "sentiment": dict(sentiment),
        "relevance": dict(relevance),
        "theme_counts": dict(theme_counts.most_common()),
        "quotes_offered": tally["quotes_offered"],
        "quotes_verified": tally["quotes_verified"],
        "quotes_unverified": len(unverified),
        "validation_problems": len(problems),
    }, indent=2))


if __name__ == "__main__":
    main()
