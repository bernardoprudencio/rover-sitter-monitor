"""Score Phase 1 — kw_r4 vs kw_r5 vs subagent on the 250-post sample.

Combines:
  - rejudge_results_*.json (190 disagreement verdicts)
  - agreement_index.json   (60 unanimous posts + 190 with hidden _sources)
  - Round 4 audit JSON     (verdicts on the 60 unanimous, where applicable)

For each of 250 posts and each of 3 strategies, decide: correct / wrong.
A strategy is "correct" on a post when:
  - It is in the unanimous-agreement bucket AND the audit didn't flag it
    (i.e. baseline-correct or no audit entry), OR
  - It is in the unanimous-agreement bucket but the audit DID flag it
    (false_positive / mixed / etc) — then ALL three strategies are equally wrong, OR
  - It is in the disagreement bucket AND the re-judge picked the option
    sourced from this strategy.

Outputs:
  - results.phase1.json (per-post verdicts joined across strategies)
  - summary.md          (scoreboard + recommendation)
"""
from __future__ import annotations

import json
from collections import Counter
from math import sqrt
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
PHASE1 = REPO_ROOT / "scripts/eval_tagger/outputs/phase1"
AUDIT_PATH = REPO_ROOT / "reviews/2026-05-05-tag-review-round4.json"
SAMPLE_PATH = PHASE1 / "sample_250.json"

STRATEGIES = ["kw_r4", "kw_r5", "subagent"]


def wilson_ci(k: int, n: int, z: float = 1.96) -> tuple[float, float]:
    if n == 0:
        return (0.0, 0.0)
    p = k / n
    denom = 1 + z**2 / n
    centre = (p + z**2 / (2 * n)) / denom
    half = z * sqrt(p * (1 - p) / n + z**2 / (4 * n**2)) / denom
    return (max(0.0, centre - half), min(1.0, centre + half))


def main():
    sample = json.loads(SAMPLE_PATH.read_text())
    sample_urls = [r["url"] for r in sample]

    # Predictions per strategy
    preds = {
        s: {r["url"]: r for r in json.loads((PHASE1 / f"predictions.{s}.json").read_text())}
        for s in STRATEGIES
    }

    audit = {r["url"]: r for r in json.loads(AUDIT_PATH.read_text())}
    agreement_index = {r["url"]: r for r in json.loads((PHASE1 / "agreement_index.json").read_text())}

    # Merge re-judge verdicts
    rejudge = {}
    for i in range(1, 5):
        for r in json.loads((PHASE1 / "rejudge_batches" / f"rejudge_results_{i}.json").read_text()):
            rejudge[r["url"]] = r

    per_post = []
    correct_counts = {s: 0 for s in STRATEGIES}
    wrong_counts = {s: 0 for s in STRATEGIES}

    for url in sample_urls:
        ai = agreement_index[url]
        post_record = {"url": url, "agreed": ai["agreed"]}

        if ai["agreed"]:
            # All 3 strategies produced the same tags. Use Round 4 audit verdict if present.
            audit_entry = audit.get(url)
            if audit_entry is None:
                # Implicitly baseline-correct
                for s in STRATEGIES:
                    correct_counts[s] += 1
                post_record["judge_source"] = "audit_implicit_correct"
                post_record["winners"] = STRATEGIES.copy()
            else:
                # Audit flagged this baseline. All three strategies share the
                # same tagging, so all three are equally wrong.
                for s in STRATEGIES:
                    wrong_counts[s] += 1
                post_record["judge_source"] = f"audit_flagged_{audit_entry['verdict']}"
                post_record["winners"] = []
                post_record["audit_proposed"] = audit_entry.get("proposed_problems")
        else:
            # Disagreement — use re-judge verdict
            rj = rejudge.get(url)
            if rj is None:
                post_record["judge_source"] = "MISSING_REJUDGE"
                post_record["winners"] = []
                per_post.append(post_record)
                continue

            verdict = rj["verdict"]  # "A" / "B" / "C" / "all_wrong"
            post_record["rejudge_verdict"] = verdict
            post_record["rejudge_rationale"] = rj.get("rationale", "")

            if verdict == "all_wrong":
                for s in STRATEGIES:
                    wrong_counts[s] += 1
                post_record["judge_source"] = "rejudge_all_wrong"
                post_record["winners"] = []
                post_record["correct_problems"] = rj.get("correct_problems")
            else:
                # Find which option (label) was chosen, then which strategies
                # produced that exact tag-set
                winning_sources = []
                for opt in ai["options"]:
                    if opt["label"] == verdict:
                        winning_sources = opt["sources"]
                        break
                for s in STRATEGIES:
                    if s in winning_sources:
                        correct_counts[s] += 1
                    else:
                        wrong_counts[s] += 1
                post_record["judge_source"] = "rejudge_pick"
                post_record["winners"] = winning_sources

        per_post.append(post_record)

    # Write per-post results
    (PHASE1 / "results.phase1.json").write_text(json.dumps(per_post, indent=2))

    # Build scoreboard
    print()
    print("=" * 78)
    print("PHASE 1 — Scoreboard (n=250)")
    print("=" * 78)
    print()
    print(f"{'Strategy':<12} {'Correct':>10} {'Wrong':>10} {'Correct %':>12} {'95% CI':>20}")
    print("-" * 78)
    rows = []
    for s in STRATEGIES:
        c = correct_counts[s]
        w = wrong_counts[s]
        n = c + w
        pct = 100 * c / n if n else 0
        lo, hi = wilson_ci(c, n)
        rows.append((s, c, w, pct, lo * 100, hi * 100))
        print(f"{s:<12} {c:>10} {w:>10} {pct:>11.1f}%  [{lo*100:>5.1f}%, {hi*100:>5.1f}%]")
    print()

    # Coverage breakdown
    n_unanim = sum(1 for r in per_post if r["agreed"])
    n_disagree = len(per_post) - n_unanim
    n_unanim_correct = sum(1 for r in per_post if r["agreed"] and r["judge_source"] == "audit_implicit_correct")
    n_unanim_flagged = n_unanim - n_unanim_correct
    n_rj_pick = sum(1 for r in per_post if r["judge_source"] == "rejudge_pick")
    n_rj_aw = sum(1 for r in per_post if r["judge_source"] == "rejudge_all_wrong")

    print("Coverage breakdown:")
    print(f"  Unanimous agreement:           {n_unanim:>3}/250  ({n_unanim_correct} baseline-correct, {n_unanim_flagged} flagged-by-audit)")
    print(f"  Re-judge picked an option:     {n_rj_pick:>3}/250")
    print(f"  Re-judge said all_wrong:       {n_rj_aw:>3}/250")
    print()

    # Where did each strategy win in the re-judge bucket?
    rj_wins = Counter()
    for r in per_post:
        if r["judge_source"] == "rejudge_pick":
            for s in r["winners"]:
                rj_wins[s] += 1
    print("Re-judge wins (out of 188 picked verdicts):")
    for s in STRATEGIES:
        print(f"  {s:<12} {rj_wins[s]:>3}")
    print()

    # Disagreement-only accuracy (drops the 60 unanimous tied posts)
    print("Re-judge bucket only (n=190; 188 picked + 2 all_wrong):")
    print(f"{'Strategy':<12} {'Won':>10} {'Lost':>10} {'Win %':>12}")
    print("-" * 50)
    for s in STRATEGIES:
        won = rj_wins[s]
        lost = (n_rj_pick + n_rj_aw) - won
        n = won + lost
        pct = 100 * won / n if n else 0
        print(f"{s:<12} {won:>10} {lost:>10} {pct:>11.1f}%")

    return rows, n_unanim_correct, n_unanim_flagged, rj_wins, n_rj_pick, n_rj_aw


if __name__ == "__main__":
    main()
