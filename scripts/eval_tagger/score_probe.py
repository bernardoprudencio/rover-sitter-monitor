"""Score the Phase-0 probe.

Joins:
  - probe_set.json     (20 posts + keyword baseline tags)
  - results.subagent.json  (subagent's tags)
Runs:
  - keyword baseline (live, via tag_post)
Prints:
  - Side-by-side table per post
  - FP-correction rate, untagged-newly-tagged rate
  - Phase-0 decision-gate verdict
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))

from rover_sheet_dump import tag_post

PROBE = REPO_ROOT / "scripts/eval_tagger/outputs/phase0/probe_set.json"
SUBAGENT = REPO_ROOT / "scripts/eval_tagger/outputs/phase0/results.subagent.json"
TAXONOMY = REPO_ROOT / "taxonomy.json"


def main():
    probe = json.loads(PROBE.read_text())
    subagent = {r["url"]: r for r in json.loads(SUBAGENT.read_text())}
    tax = json.loads(TAXONOMY.read_text())
    valid_themes = set(tax["themes"]) | {"Untagged"}
    valid_problems = set(tax["problems"].keys()) | {"Untagged"}

    # Build joined rows
    rows = []
    for r in probe:
        sub = subagent.get(r["url"], {})
        kw_themes, kw_problems = tag_post(r["title"], r["preview"])
        rows.append({
            **r,
            "kw_themes": kw_themes,
            "kw_problems": kw_problems,
            "sub_themes": sub.get("themes", []),
            "sub_problems": sub.get("problems", []),
            "sub_rationale": sub.get("rationale", ""),
        })

    # Validation
    halluc = []
    for row in rows:
        for t in row["sub_themes"]:
            if t not in valid_themes:
                halluc.append((row["url"], "theme", t))
        for p in row["sub_problems"]:
            if p not in valid_problems:
                halluc.append((row["url"], "problem", p))

    # FP correction: subagent does NOT re-fire the SPECIFIC FP problem(s).
    # FP set = current_problems - proposed_problems (per Round-4 audit).
    fps = [r for r in rows if r["kind"] == "fp"]
    untagged = [r for r in rows if r["kind"] == "untagged"]

    fps_corrected = 0
    fp_details = []
    for r in fps:
        proposed = set(r.get("audit_proposed_problems") or [])
        current = set(r["current_problems"])
        fp_set = current - proposed
        re_fired = fp_set & set(r["sub_problems"])
        corrected = not re_fired
        fps_corrected += corrected
        fp_details.append((r, corrected, re_fired, fp_set, proposed))

    untagged_newly_tagged = 0
    untagged_details = []
    for r in untagged:
        newly = r["sub_problems"] != ["Untagged"]
        untagged_newly_tagged += newly
        untagged_details.append((r, newly))

    # Print
    print("=" * 100)
    print("PHASE 0 — Keyword baseline vs Claude Code subagent (20 posts)")
    print("=" * 100)
    print()
    print("--- KNOWN FALSE POSITIVES (10) ---")
    print("Goal: subagent should NOT re-fire the SPECIFIC FP problem(s)")
    print("(FP set = current_problems − audit-proposed_problems).")
    print()
    for r, corrected, re_fired, fp_set, proposed in fp_details:
        flag = "✓ corrected" if corrected else f"✗ re-fired FP {sorted(re_fired)}"
        print(f"  {flag}")
        print(f"    title:    {r['title'][:80]}")
        print(f"    KW:       {r['kw_problems']}")
        print(f"    audit-FP: {sorted(fp_set)}    audit-keep: {sorted(proposed)}")
        print(f"    SUB:      {r['sub_problems']}")
        print(f"    audit:    {r['audit_rationale']}")
        print(f"    sub-why:  {r['sub_rationale']}")
        print()

    print("--- UNTAGGED POSTS (10) ---")
    print("Goal: subagent should propose plausible tags where keyword returned Untagged.")
    print()
    for r, newly in untagged_details:
        flag = "✓ newly tagged" if newly else "  still untagged"
        print(f"  {flag}")
        print(f"    title:   {r['title'][:80]}")
        print(f"    SUB:     problems={r['sub_problems']}")
        print(f"    sub-why: {r['sub_rationale']}")
        print()

    # Gate
    print("=" * 100)
    print("DECISION GATE")
    print("=" * 100)
    print(f"  FP correction:           {fps_corrected}/10  (gate: ≥7)")
    print(f"  Untagged newly tagged:   {untagged_newly_tagged}/10")
    print(f"    (no judge here — subagent's own rationale is the only signal)")
    print(f"  Hallucinated names:      {len(halluc)}")
    if halluc:
        for url, kind, name in halluc:
            print(f"    - {kind}: {name!r}  ({url})")
    print()
    print(f"  Notes on the untagged sample:")
    print(f"  - This was a uniform-random draw from untagged posts, not a hand-picked")
    print(f"    'on-topic' set. Many genuinely don't fit the taxonomy (Q&A, venting).")
    print(f"  - The 'recall recovery' signal is qualitative until Phase 1 re-judge.")
    print()
    if fps_corrected >= 7:
        verdict = "PASS on FP signal — proceed to Phase 1 to measure recall properly."
    else:
        verdict = "FAIL — subagent does not clearly beat keywords on FPs; re-evaluate."
    print(f"  VERDICT: {verdict}")


if __name__ == "__main__":
    main()
