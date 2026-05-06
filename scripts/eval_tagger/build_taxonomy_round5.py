"""Build taxonomy_round5.json by applying the Round 5 plan to taxonomy.json.

Source of changes: reviews/2026-05-05-tag-review-round4.md, "Round 5 plan" section.
Pure overlay — does not modify the live taxonomy.json.
"""
from __future__ import annotations

import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
SRC = REPO_ROOT / "taxonomy.json"
DST = REPO_ROOT / "scripts" / "eval_tagger" / "taxonomy_round5.json"


def replace_keywords(taxonomy: dict, problem: str, drop: list[str], add: list[str]):
    """Drop listed keywords from a problem, then add new ones (deduped)."""
    p = taxonomy["problems"][problem]
    kws = [k for k in p["keywords"] if k not in drop]
    for k in add:
        if k not in kws:
            kws.append(k)
    p["keywords"] = kws


def main():
    tax = json.loads(SRC.read_text())

    # 1. Cats and kittens — drop bare 'cat', add specific phrases
    replace_keywords(tax, "Cats and kittens",
        drop=["cat"],
        add=["cat sitter", "cat sitting", "cat boarding", "cat owner", "cat client",
             "kitty", "kitties", "cat drop", "cat litter", "cat parent"])

    # 2. High quality pet care — narrow 'training'
    replace_keywords(tax, "High quality pet care",
        drop=["training"],
        add=["sitter training", "pet care training", "training certification",
             "training course", "dog trainer", "behavior training"])

    # 3. Breeds — narrow 'breed'
    replace_keywords(tax, "Breeds",
        drop=["breed"],
        add=["breed restriction", "dog breed", "breed list", "breed concern",
             "specific breed", "which breeds", "bully breed", "breed ban", "breed restricted"])

    # 4. Time off / holidays — narrow 'unavailable'
    replace_keywords(tax, "Time off / holidays",
        drop=["unavailable"],
        add=["mark unavailable", "set unavailable", "block unavailable",
             "i'm unavailable", "not available those dates"])

    # 5a. Low demand — narrow 'more clients'
    replace_keywords(tax, "Low demand",
        drop=["more clients"],
        add=["not enough clients", "need more clients", "getting fewer clients"])

    # 5b. Navigation — narrow 'navigate' / 'can't find'
    replace_keywords(tax, "Navigation",
        drop=["navigate", "can't find"],
        add=["navigate the app", "navigate rover", "navigate menu", "navigate website",
             "can't find feature", "can't find setting", "can't find page",
             "can't find option", "where is the", "hard to find feature"])

    # 6a. Business insurance — narrow 'insurance' and drop 'protect'
    replace_keywords(tax, "Business insurance",
        drop=["insurance", "protect"],
        add=["pet insurance", "business insurance", "liability insurance",
             "sitter insurance", "pet care insurance", "insurance for"])

    # 6b. Lost or injured pet — narrow 'neglected' / 'neglects'
    replace_keywords(tax, "Lost or injured pet",
        drop=["neglected", "neglects"],
        add=["pet neglected", "dog neglected", "cat neglected",
             "obvious neglect", "severe neglect", "neglectful sitter"])

    # 6c. Distance — narrow 'distance'
    replace_keywords(tax, "Distance",
        drop=["distance"],
        add=["service distance", "travel distance", "walk distance",
             "driving distance", "commute distance"])

    DST.write_text(json.dumps(tax, indent=2))
    print(f"Wrote {DST}")
    # Sanity check
    src_kw_count = sum(len(p["keywords"]) for p in json.loads(SRC.read_text())["problems"].values())
    dst_kw_count = sum(len(p["keywords"]) for p in tax["problems"].values())
    print(f"R4 keyword count: {src_kw_count}")
    print(f"R5 keyword count: {dst_kw_count}")
    print(f"Net change: {dst_kw_count - src_kw_count:+d}")


if __name__ == "__main__":
    main()
