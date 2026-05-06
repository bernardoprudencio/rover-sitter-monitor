"""Phase-0 quick probe: keyword baseline vs LLM tagger on 20 posts.

Runs:
  - keyword baseline (imports tag_post from rover_sheet_dump)
  - LLM tagger (Haiku 4.5 by default; --model to override)

Outputs:
  - outputs/phase0/results.<model>.json   (full per-post records)
  - stdout: side-by-side table + cost summary + decision-gate verdict

Decision gate (per plan):
  - Of 10 known-FP posts: LLM "corrects" if it does NOT re-fire the FP problem.
    Pass: >=7 of 10 corrected.
  - Of 10 untagged posts: LLM "tags plausibly" if it returns >=1 problem
    (no judgment of plausibility — that's eyeballed by reviewing output).
    Pass: >=7 of 10 newly tagged. Plausibility verified by reading the printout.

Usage:
  ANTHROPIC_API_KEY=sk-... python3 scripts/eval_tagger/quick_probe.py
  ANTHROPIC_API_KEY=sk-... python3 scripts/eval_tagger/quick_probe.py --model claude-sonnet-4-5
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))

from rover_sheet_dump import tag_post
from scripts.eval_tagger.taggers.llm_claude import LLMTagger, DEFAULT_MODEL

PROBE_PATH = REPO_ROOT / "scripts" / "eval_tagger" / "outputs" / "phase0" / "probe_set.json"

# Haiku 4.5 pricing per 1M tokens
PRICE = {
    "claude-haiku-4-5":  {"input": 1.0,  "output": 5.0,  "cache_read": 0.10, "cache_write": 1.25},
    "claude-sonnet-4-5": {"input": 3.0,  "output": 15.0, "cache_read": 0.30, "cache_write": 3.75},
}


def cost_usd(model: str, r) -> float:
    p = PRICE.get(model, PRICE["claude-haiku-4-5"])
    uncached_input = max(0, r.input_tokens - r.cache_read_tokens - r.cache_creation_tokens)
    return (
        uncached_input          * p["input"]       / 1e6
      + r.cache_read_tokens     * p["cache_read"]  / 1e6
      + r.cache_creation_tokens * p["cache_write"] / 1e6
      + r.output_tokens         * p["output"]      / 1e6
    )


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default=DEFAULT_MODEL)
    ap.add_argument("--probe", type=Path, default=PROBE_PATH)
    args = ap.parse_args()

    rows = json.loads(args.probe.read_text())
    tagger = LLMTagger(model=args.model)

    results = []
    total_cost = 0.0
    for i, row in enumerate(rows, 1):
        kw_themes, kw_problems = tag_post(row["title"], row["preview"])
        llm = tagger.tag(row["title"], row["preview"])
        c = cost_usd(args.model, llm)
        total_cost += c
        results.append({
            "kind": row["kind"],
            "url": row["url"],
            "title": row["title"],
            "preview": row["preview"],
            "current_problems": row["current_problems"],
            "current_themes": row["current_themes"],
            "audit_proposed_problems": row.get("audit_proposed_problems"),
            "audit_rationale": row.get("audit_rationale"),
            "kw_themes": kw_themes,
            "kw_problems": kw_problems,
            "llm_themes": llm.themes,
            "llm_problems": llm.problems,
            "llm_cache_read_tokens": llm.cache_read_tokens,
            "llm_cache_creation_tokens": llm.cache_creation_tokens,
            "llm_input_tokens": llm.input_tokens,
            "llm_output_tokens": llm.output_tokens,
            "llm_latency_ms": round(llm.latency_ms, 1),
            "llm_cost_usd": round(c, 6),
            "llm_hallucinated": llm.hallucinated,
            "llm_error": llm.error,
            "llm_raw": llm.raw_response,
        })
        marker = "FP " if row["kind"] == "fp" else "UNT"
        print(f"[{i:2d}/{len(rows)}] {marker} {row['title'][:50]:50s} -> {','.join(llm.problems)[:40]}")

    out_path = args.probe.parent / f"results.{args.model.replace('claude-','')}.json"
    out_path.write_text(json.dumps(results, indent=2))

    # Score the gate
    fp_results = [r for r in results if r["kind"] == "fp"]
    unt_results = [r for r in results if r["kind"] == "untagged"]

    fps_corrected = sum(
        1 for r in fp_results
        if not (set(r["current_problems"]) & set(r["llm_problems"]))
    )
    unt_newly_tagged = sum(
        1 for r in unt_results
        if r["llm_problems"] != ["Untagged"]
    )
    hallucinations = sum(len(r["llm_hallucinated"]) for r in results)

    print()
    print("=" * 78)
    print(f"Model:                    {args.model}")
    print(f"Total cost (20 posts):    ${total_cost:.4f}")
    print(f"Avg cost/post:            ${total_cost/len(results):.5f}")
    print(f"Cache hit (read tokens):  {sum(r['llm_cache_read_tokens'] for r in results):,}")
    print(f"Cache write tokens:       {sum(r['llm_cache_creation_tokens'] for r in results):,}")
    print(f"Hallucinated names:       {hallucinations}")
    print()
    print(f"FP correction rate:       {fps_corrected}/10  (gate: >=7)")
    print(f"Untagged newly tagged:    {unt_newly_tagged}/10  (gate: >=7)")
    print()
    if fps_corrected >= 7 and unt_newly_tagged >= 7:
        print("GATE PASSED -> proceed to Phase 1 (full 250-post eval).")
    else:
        print("GATE NOT PASSED -> review printout; consider escalating to Sonnet.")
    print(f"\nFull results written to: {out_path}")


if __name__ == "__main__":
    main()
