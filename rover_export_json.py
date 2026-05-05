#!/usr/bin/env python3
"""Read sheet → emit hashed JSON dataset for the dashboard.

Writes 4 files atomically into --out:
    posts.<hash>.json       (array)
    aggregates.<hash>.json  (object)
    taxonomy.json           (verbatim copy of repo-root taxonomy)
    meta.json               (index, written LAST)

Auth reuses get_sheet() from rover_sheet_dump.py (GOOGLE_CREDS_JSON env or CREDS_FILE).
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
from collections import Counter, defaultdict
from datetime import datetime, timezone
from typing import Optional

SCHEMA_VERSION = 1
PREVIEW_MAX = 500

# Inline stopword set (no nltk dependency).
STOPWORDS = {
    "the", "a", "an", "and", "or", "but", "is", "are", "was", "were", "be", "been",
    "i", "you", "my", "we", "they", "it", "this", "that", "of", "to", "in", "on", "for",
    "with", "at", "by", "as", "from", "have", "has", "had", "do", "does", "did", "not",
    "no", "so", "if", "when", "then", "just", "like", "get", "got", "one", "really",
    "would", "could", "should", "can", "will", "your", "her", "his", "their", "our",
    "me", "us", "him", "them", "she", "he", "who", "what", "why", "how", "all", "any",
    "some", "out", "up", "down", "about", "into", "than", "too", "very", "also", "now",
    "there", "here", "more", "most", "much", "even", "want", "need", "know",
}

_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))


def truncate_preview(s: str) -> str:
    """Truncate to PREVIEW_MAX chars, never breaking mid-word; append … if cut."""
    if not s:
        return ""
    if len(s) <= PREVIEW_MAX:
        return s
    cut = s[:PREVIEW_MAX]
    sp = cut.rfind(" ")
    return (cut[:sp] if sp > 0 else cut).rstrip() + "…"


def parse_row(row) -> Optional[dict]:
    """Parse a sheet row into a post dict. Returns None if row is malformed.

    Sheet columns: Date | Title | URL | Author | Preview | Themes | Problems | Subreddit
    """
    if len(row) < 8 or not row[2]:
        return None
    try:
        dt = datetime.strptime(row[0], "%Y-%m-%d %H:%M UTC").replace(tzinfo=timezone.utc)
    except ValueError:
        return None
    themes = [t for t in (row[5] or "").split(", ") if t]
    problems = [p for p in (row[6] or "").split(", ") if p]
    return {
        "id": hashlib.sha1(row[2].encode()).hexdigest()[:10],
        "date": dt.strftime("%Y-%m-%d"),
        "title": row[1],
        "url": row[2],
        "author": row[3],
        "preview": truncate_preview(row[4] or ""),
        "themes": themes,
        "problems": problems,
        "subreddit": row[7],
    }


def top_keywords(texts, n: int = 50):
    """Top-n unigrams + bigrams from texts after stopword removal."""
    freq: Counter = Counter()
    for t in texts:
        words = [w for w in re.findall(r"[a-z']{3,}", (t or "").lower()) if w not in STOPWORDS]
        freq.update(words)
        freq.update(f"{a} {b}" for a, b in zip(words, words[1:]))
    return [{"word": w, "count": c} for w, c in freq.most_common(n)]


def build_aggregates(posts) -> dict:
    """Precompute aggregates for instant Overview/Trends render.

    Multi-theme posts increment BOTH theme bars (correct signal) but count
    ONCE in totalTaggedPosts (distinct-post denominator).
    """
    themes_by_day: defaultdict = defaultdict(lambda: defaultdict(int))
    problems_by_day: defaultdict = defaultdict(lambda: defaultdict(int))
    theme_counts: Counter = Counter()
    problem_counts: Counter = Counter()
    untagged_text = []
    total_tagged = 0

    for p in posts:
        if p["themes"] == ["Untagged"]:
            untagged_text.append(p["preview"])
            continue
        total_tagged += 1
        for t in p["themes"]:
            themes_by_day[t][p["date"]] += 1
            theme_counts[t] += 1
        for pr in p["problems"]:
            problems_by_day[pr][p["date"]] += 1
            problem_counts[pr] += 1

    # Convert nested defaultdicts to plain dicts for JSON serialization.
    return {
        "themesByDay": {k: dict(v) for k, v in themes_by_day.items()},
        "problemsByDay": {k: dict(v) for k, v in problems_by_day.items()},
        "themeCounts": dict(theme_counts),
        "problemCounts": dict(problem_counts),
        "untaggedCount": len(untagged_text),
        "untaggedKeywordFreq": top_keywords(untagged_text, n=50),
        "totalPosts": len(posts),
        "totalTaggedPosts": total_tagged,
    }


def hashed_name(stem: str, content) -> str:
    """sha1(json.dumps(content, sort_keys=True))[:8] for cache-busting."""
    h = hashlib.sha1(json.dumps(content, sort_keys=True).encode()).hexdigest()[:8]
    return f"{stem}.{h}.json"


def atomic_write(out_dir: str, filename: str, content) -> None:
    """Write tmp file then os.replace — never leaves a half-written file."""
    tmp = os.path.join(out_dir, f".tmp_{filename}")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(content, f, ensure_ascii=False)
    os.replace(tmp, os.path.join(out_dir, filename))


def write_dataset(posts, taxonomy, out_dir: str) -> dict:
    """Write the 4-file dataset to out_dir. Returns the meta dict."""
    os.makedirs(out_dir, exist_ok=True)
    aggs = build_aggregates(posts)

    posts_name = hashed_name("posts", {"p": posts})
    aggs_name = hashed_name("aggregates", aggs)

    atomic_write(out_dir, posts_name, posts)
    atomic_write(out_dir, aggs_name, aggs)
    atomic_write(out_dir, "taxonomy.json", taxonomy)

    if posts:
        date_range = {"start": posts[0]["date"], "end": posts[-1]["date"]}
    else:
        date_range = {"start": None, "end": None}

    meta = {
        "schema_version": SCHEMA_VERSION,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "post_count": len(posts),
        "date_range": date_range,
        "posts_file": posts_name,
        "aggregates_file": aggs_name,
    }
    # meta.json LAST — a crashed run never leaves a partial dataset visible.
    atomic_write(out_dir, "meta.json", meta)
    return meta


def load_taxonomy() -> dict:
    """Read taxonomy.json from the same dir as this script."""
    with open(os.path.join(_SCRIPT_DIR, "taxonomy.json"), "r", encoding="utf-8") as f:
        return json.load(f)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--out", required=True, help="Output directory for JSON files")
    args = ap.parse_args()

    # Defensive: refuse to write into a built dist/ directory.
    assert "dist" not in os.path.abspath(args.out).split(os.sep), \
        "Refusing to write into dist/"

    # Lazy import — only the live export needs gspread; fixture generation reuses
    # the helpers above without paying for the dep.
    from rover_sheet_dump import get_sheet  # noqa: WPS433

    ws = get_sheet()
    rows = ws.get_all_values()[1:]  # skip header
    posts = sorted(
        (p for p in (parse_row(r) for r in rows) if p),
        key=lambda p: p["date"],
    )
    taxonomy = load_taxonomy()
    meta = write_dataset(posts, taxonomy, args.out)
    print(f"Wrote {meta['post_count']} posts → {args.out}")
    print(f"  posts:      {meta['posts_file']}")
    print(f"  aggregates: {meta['aggregates_file']}")
    print(f"  date range: {meta['date_range']['start']} → {meta['date_range']['end']}")


if __name__ == "__main__":
    main()
