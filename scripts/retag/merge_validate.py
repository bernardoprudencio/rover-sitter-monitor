"""Merge subagent batch outputs and validate against taxonomy.

Used by both /retag-new and /retag-all. Writes:
  - merged JSON [{url, themes, problems, rationale}, ...]
  - hallucinations log if any names weren't in the taxonomy
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
TAX = REPO_ROOT / "taxonomy.json"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--batch-glob", required=True,
                    help="Glob for subagent result files, e.g. /tmp/retag_results_*.json")
    ap.add_argument("--out", required=True, help="Merged output path")
    ap.add_argument("--halluc-log", default=None, help="Optional hallucinations log path")
    args = ap.parse_args()

    tax = json.loads(TAX.read_text())
    valid_themes = set(tax["themes"]) | {"Untagged"}
    valid_problems = set(tax["problems"].keys()) | {"Untagged"}
    problem_to_theme = {p: meta["theme"] for p, meta in tax["problems"].items()}

    import glob
    files = sorted(glob.glob(args.batch_glob))
    if not files:
        raise SystemExit(f"No files match {args.batch_glob}")

    merged = []
    halluc = []
    seen_urls = set()
    for fp in files:
        for row in json.loads(Path(fp).read_text()):
            url = row.get("url")
            if not url or url in seen_urls:
                continue
            seen_urls.add(url)
            cleaned_themes, cleaned_problems = [], []
            for t in row.get("themes", []) or []:
                if t in valid_themes:
                    if t not in cleaned_themes:
                        cleaned_themes.append(t)
                else:
                    halluc.append({"url": url, "kind": "theme", "value": t})
            for p in row.get("problems", []) or []:
                if p in valid_problems:
                    if p not in cleaned_problems:
                        cleaned_problems.append(p)
                    parent = problem_to_theme.get(p)
                    if parent and parent not in cleaned_themes:
                        cleaned_themes.append(parent)
                else:
                    halluc.append({"url": url, "kind": "problem", "value": p})
            if not cleaned_themes:
                cleaned_themes = ["Untagged"]
            if not cleaned_problems:
                cleaned_problems = ["Untagged"]
            merged.append({
                "url": url,
                "themes": cleaned_themes,
                "problems": cleaned_problems,
                "rationale": row.get("rationale", ""),
            })

    Path(args.out).write_text(json.dumps(merged, indent=2))
    untagged = sum(1 for r in merged if r["problems"] == ["Untagged"])
    multi = sum(1 for r in merged if len(r["problems"]) > 1)
    print(f"Merged {len(merged)} rows -> {args.out}  (untagged={untagged}, multi={multi}, hallucinations={len(halluc)})")
    if halluc and args.halluc_log:
        Path(args.halluc_log).write_text(json.dumps(halluc, indent=2))
        print(f"Hallucinations logged to {args.halluc_log}")


if __name__ == "__main__":
    main()
