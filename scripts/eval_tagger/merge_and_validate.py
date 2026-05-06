"""Merge 5 batch results into predictions.subagent.json and validate against taxonomy."""
from __future__ import annotations

import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
PHASE1 = REPO_ROOT / "scripts/eval_tagger/outputs/phase1"
TAX = REPO_ROOT / "taxonomy.json"


def main():
    tax = json.loads(TAX.read_text())
    valid_themes = set(tax["themes"]) | {"Untagged"}
    valid_problems = set(tax["problems"].keys()) | {"Untagged"}
    problem_to_theme = {p: meta["theme"] for p, meta in tax["problems"].items()}

    sample = json.loads((PHASE1 / "sample_250.json").read_text())
    sample_urls = [r["url"] for r in sample]

    merged = []
    halluc = []
    for i in range(1, 6):
        batch = json.loads((PHASE1 / "batches" / f"results_{i}.json").read_text())
        for row in batch:
            cleaned_themes = []
            cleaned_problems = []
            for t in row.get("themes", []):
                if t in valid_themes:
                    if t not in cleaned_themes:
                        cleaned_themes.append(t)
                else:
                    halluc.append({"url": row["url"], "kind": "theme", "value": t})
            for p in row.get("problems", []):
                if p in valid_problems:
                    if p not in cleaned_problems:
                        cleaned_problems.append(p)
                    # Auto-add parent theme if missing
                    parent = problem_to_theme.get(p)
                    if parent and parent not in cleaned_themes:
                        cleaned_themes.append(parent)
                else:
                    halluc.append({"url": row["url"], "kind": "problem", "value": p})
            if not cleaned_themes:
                cleaned_themes = ["Untagged"]
            if not cleaned_problems:
                cleaned_problems = ["Untagged"]
            merged.append({
                "url": row["url"],
                "themes": cleaned_themes,
                "problems": cleaned_problems,
                "rationale": row.get("rationale", ""),
            })

    # Re-order to match sample order
    by_url = {r["url"]: r for r in merged}
    missing = [u for u in sample_urls if u not in by_url]
    if missing:
        print(f"WARNING: {len(missing)} sample URLs missing from subagent results: {missing[:5]}")
    ordered = [by_url[u] for u in sample_urls if u in by_url]

    out = PHASE1 / "predictions.subagent.json"
    out.write_text(json.dumps(ordered, indent=2))
    print(f"Wrote {out.name}: {len(ordered)} rows")
    print(f"Hallucinations: {len(halluc)}")
    if halluc:
        for h in halluc[:10]:
            print(f"  - {h['kind']}: {h['value']!r}  ({h['url']})")
    untagged = sum(1 for r in ordered if r["problems"] == ["Untagged"])
    multi = sum(1 for r in ordered if len(r["problems"]) > 1)
    print(f"Untagged: {untagged}, multi-tag: {multi}")

    if halluc:
        (PHASE1 / "subagent_hallucinations.json").write_text(json.dumps(halluc, indent=2))


if __name__ == "__main__":
    main()
