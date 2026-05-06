"""Run keyword tagger (R4 + R5 taxonomies) on the 250-post sample.

Writes:
  outputs/phase1/predictions.kw_r4.json
  outputs/phase1/predictions.kw_r5.json
"""
from __future__ import annotations

import json
import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
SAMPLE = REPO_ROOT / "scripts/eval_tagger/outputs/phase1/sample_250.json"
TAX_R4 = REPO_ROOT / "taxonomy.json"
TAX_R5 = REPO_ROOT / "scripts/eval_tagger/taxonomy_round5.json"
OUT_DIR = REPO_ROOT / "scripts/eval_tagger/outputs/phase1"


def tag_with(taxonomy: dict, title: str, text: str) -> tuple[list[str], list[str]]:
    """Pure-function reimplementation of tag_post that takes taxonomy as arg."""
    combined = (title + " " + text).lower()
    problems_kw = {p: meta["keywords"] for p, meta in taxonomy["problems"].items()}
    problem_to_theme = {p: meta["theme"] for p, meta in taxonomy["problems"].items()}

    matched_problems, matched_themes = [], []
    for problem, keywords in problems_kw.items():
        for kw in keywords:
            if re.search(r'\b' + re.escape(kw) + r'\b', combined):
                matched_problems.append(problem)
                theme = problem_to_theme.get(problem)
                if theme and theme not in matched_themes:
                    matched_themes.append(theme)
                break
    return (
        matched_themes if matched_themes else ["Untagged"],
        matched_problems if matched_problems else ["Untagged"],
    )


def run(taxonomy_path: Path, out_path: Path):
    tax = json.loads(taxonomy_path.read_text())
    sample = json.loads(SAMPLE.read_text())
    results = []
    for row in sample:
        themes, problems = tag_with(tax, row["title"], row["preview"])
        results.append({"url": row["url"], "themes": themes, "problems": problems})
    out_path.write_text(json.dumps(results, indent=2))
    untagged = sum(1 for r in results if r["problems"] == ["Untagged"])
    multi = sum(1 for r in results if len(r["problems"]) > 1)
    print(f"  wrote {out_path.name}: {len(results)} rows, untagged={untagged}, multi={multi}")


if __name__ == "__main__":
    print(f"Sample: {SAMPLE}")
    print("R4:")
    run(TAX_R4, OUT_DIR / "predictions.kw_r4.json")
    print("R5:")
    run(TAX_R5, OUT_DIR / "predictions.kw_r5.json")
