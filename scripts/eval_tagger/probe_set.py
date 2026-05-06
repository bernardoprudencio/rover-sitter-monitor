"""Build the 20-post Phase-0 probe set: 10 known-FPs + 10 untagged samples.

Deterministic. Reads from:
  - reviews/2026-05-05-tag-review-round4.json  (FP source)
  - dashboard posts JSON (body source — looked up across all worktrees,
    falls back to the most recent file matching posts.*.json)
"""
from __future__ import annotations

import json
import random
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
PARENT_REPO = Path("/Users/bernardoprudencio/Documents/rover-repo/rover-sitter-monitor")

AUDIT_PATH = REPO_ROOT / "reviews" / "2026-05-05-tag-review-round4.json"
SEED = 20260505
N_FP = 10
N_UNTAGGED = 10
MIN_PREVIEW_LEN = 150
MIN_TITLE_LEN = 20


def find_posts_json() -> Path:
    candidates = sorted(
        PARENT_REPO.glob(".claude/worktrees/*/dashboard/public/data/posts.*.json"),
        key=lambda p: p.stat().st_mtime,
        reverse=True,
    )
    if not candidates:
        raise FileNotFoundError("No posts.*.json found in any worktree's dashboard/public/data/")
    return candidates[0]


def load_audit_fps() -> list[dict]:
    audit = json.loads(AUDIT_PATH.read_text())
    fps = [e for e in audit if e["verdict"] == "false_positive"]
    fps.sort(key=lambda e: e["url"])
    return fps[:N_FP]


def load_posts_by_url() -> dict[str, dict]:
    posts_path = find_posts_json()
    posts = json.loads(posts_path.read_text())
    return {p["url"]: p for p in posts}, posts_path


def sample_untagged(posts: list[dict]) -> list[dict]:
    pool = [
        p for p in posts
        if p.get("themes") == ["Untagged"]
        and len(p.get("preview", "")) >= MIN_PREVIEW_LEN
        and len(p.get("title", "")) >= MIN_TITLE_LEN
    ]
    pool.sort(key=lambda p: p["url"])
    return random.Random(SEED).sample(pool, N_UNTAGGED)


def build_probe_set() -> list[dict]:
    by_url, posts_path = load_posts_by_url()
    posts = list(by_url.values())

    fps = load_audit_fps()
    fp_rows = []
    for fp in fps:
        post = by_url.get(fp["url"])
        if post is None:
            fp_rows.append({
                "kind": "fp",
                "url": fp["url"],
                "title": fp["title"],
                "preview": "",
                "current_problems": fp["current_problems"],
                "current_themes": fp["current_themes"],
                "audit_proposed_problems": fp["proposed_problems"],
                "audit_proposed_themes": fp["proposed_themes"],
                "audit_rationale": fp["rationale"],
            })
            continue
        fp_rows.append({
            "kind": "fp",
            "url": fp["url"],
            "title": post["title"],
            "preview": post.get("preview", ""),
            "current_problems": fp["current_problems"],
            "current_themes": fp["current_themes"],
            "audit_proposed_problems": fp["proposed_problems"],
            "audit_proposed_themes": fp["proposed_themes"],
            "audit_rationale": fp["rationale"],
        })

    untagged = sample_untagged(posts)
    untagged_rows = [
        {
            "kind": "untagged",
            "url": p["url"],
            "title": p["title"],
            "preview": p.get("preview", ""),
            "current_problems": p["problems"],
            "current_themes": p["themes"],
        }
        for p in untagged
    ]

    return fp_rows + untagged_rows, posts_path


if __name__ == "__main__":
    rows, src = build_probe_set()
    out_dir = REPO_ROOT / "scripts" / "eval_tagger" / "outputs" / "phase0"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "probe_set.json"
    out_path.write_text(json.dumps(rows, indent=2))
    print(f"Posts source: {src}")
    print(f"Wrote {len(rows)} rows to {out_path}")
    print(f"  FPs:      {sum(1 for r in rows if r['kind'] == 'fp')}")
    print(f"  Untagged: {sum(1 for r in rows if r['kind'] == 'untagged')}")
