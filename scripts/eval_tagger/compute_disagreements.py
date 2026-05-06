"""Compute disagreements across kw_r4 / kw_r5 / subagent.

For each of 250 posts:
  - If all three strategies produce the same problem-set, the post is in
    'agreement' bucket. Use Round 4 audit verdict if available, else assume
    baseline-correct.
  - Otherwise, queue for re-judge with blind-shuffled options.

Writes:
  - rejudge_input.json   (input for the re-judge subagent)
  - agreement_index.json (post -> {agreed, options_count})
"""
from __future__ import annotations

import json
import random
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
PHASE1 = REPO_ROOT / "scripts/eval_tagger/outputs/phase1"
SAMPLE = PHASE1 / "sample_250.json"
AUDIT = REPO_ROOT / "reviews" / "2026-05-05-tag-review-round4.json"

SEED = 20260505


def main():
    sample = json.loads(SAMPLE.read_text())
    kw_r4 = {r["url"]: r for r in json.loads((PHASE1 / "predictions.kw_r4.json").read_text())}
    kw_r5 = {r["url"]: r for r in json.loads((PHASE1 / "predictions.kw_r5.json").read_text())}
    sub = {r["url"]: r for r in json.loads((PHASE1 / "predictions.subagent.json").read_text())}
    audit = {r["url"]: r for r in json.loads(AUDIT.read_text())}

    rng = random.Random(SEED)

    rejudge_input = []
    agreement_index = []

    for row in sample:
        url = row["url"]
        r4 = sorted(kw_r4[url]["problems"])
        r5 = sorted(kw_r5[url]["problems"])
        sb = sorted(sub[url]["problems"])

        # Build distinct options (set-equality)
        sources_per_option = {}
        for label, tags in [("kw_r4", r4), ("kw_r5", r5), ("subagent", sb)]:
            key = tuple(tags)
            sources_per_option.setdefault(key, []).append(label)

        if len(sources_per_option) == 1:
            # All three agree
            audit_entry = audit.get(url)
            agreement_index.append({
                "url": url,
                "agreed": True,
                "tags": r4,
                "audit_verdict": audit_entry.get("verdict") if audit_entry else "baseline_correct",
                "audit_proposed_problems": audit_entry.get("proposed_problems") if audit_entry else None,
                "audit_rationale": audit_entry.get("rationale") if audit_entry else None,
            })
            continue

        # Disagreement — build blind-shuffled options
        opts = list(sources_per_option.items())
        rng.shuffle(opts)
        labeled = []
        labels = ["A", "B", "C", "D"]
        for letter, (tags_tuple, srcs) in zip(labels, opts):
            labeled.append({
                "label": letter,
                "problems": list(tags_tuple),
                # _sources is hidden from the re-judge subagent during the call
                # but kept in this file for post-hoc analysis
                "_sources": srcs,
            })
        rejudge_input.append({
            "url": url,
            "title": row["title"],
            "preview": row["preview"],
            "options": labeled,
        })
        agreement_index.append({
            "url": url,
            "agreed": False,
            "options_count": len(opts),
            "options": [{"label": l["label"], "sources": l["_sources"], "problems": l["problems"]}
                        for l in labeled],
        })

    (PHASE1 / "rejudge_input.json").write_text(json.dumps(rejudge_input, indent=2))
    (PHASE1 / "agreement_index.json").write_text(json.dumps(agreement_index, indent=2))

    n_agree = sum(1 for r in agreement_index if r["agreed"])
    n_disagree = len(agreement_index) - n_agree
    print(f"Agreement (all 3 strategies match): {n_agree}/250")
    print(f"Disagreement (need re-judge):       {n_disagree}/250")
    print()
    # Distribution by option count
    by_count = {}
    for r in agreement_index:
        if not r["agreed"]:
            by_count[r["options_count"]] = by_count.get(r["options_count"], 0) + 1
    for k in sorted(by_count):
        print(f"  {k} distinct options: {by_count[k]} posts")
    print()
    print(f"Wrote rejudge_input.json ({n_disagree} posts) — ready for re-judge subagent.")


if __name__ == "__main__":
    main()
