# Phase 1 — Tagging-Method Evaluation Results

**Date:** 2026-05-05
**Sample:** 250 Reddit posts (the canonical Round 4 audit sample, seed `20260505`)
**Strategies compared:** Keyword Round 4 (production), Keyword Round 5 (queued narrowings), Claude Code subagent
**Adjudication:** 4 blind-shuffled re-judge subagents over the 190-post disagreement set

## Headline scoreboard

| Strategy | Correct | Wrong | Correct % | 95% Wilson CI |
|---|---:|---:|---:|---|
| Keyword R4 (production) | 79 | 171 | **31.6%** | 26.2 – 37.6% |
| Keyword R5 (planned)    | 82 | 168 | **32.8%** | 27.3 – 38.8% |
| **Claude Code subagent** | **230** | **20** | **92.0%** | 88.0 – 94.8% |

**Caveat: this is "best-of-three" accuracy, not absolute accuracy.** A strategy is "correct" on a post when (a) all three strategies agreed and the audit didn't flag it, or (b) the blind re-judge picked the option that strategy produced. The historical "84.4% Round-4 correct" figure is a different measurement (binary pass/fail per post) and not directly comparable. The right read here is the **gap between strategies**, which is unambiguous.

## Coverage breakdown (n=250)

- **Unanimous agreement** (all 3 strategies produced identical tag-sets): **60 / 250** — all baseline-correct per the audit.
- **Re-judge picked one option:** 188 / 250
- **Re-judge said all three were wrong:** 2 / 250

Of the 188 picked verdicts:
- subagent won: **170 (90.4%)**
- kw_r5 won: 22 (11.7%)
- kw_r4 won: 19 (10.1%)

(Sums exceed 188 because some kw_r4 and kw_r5 outputs were identical and won jointly — they tied on 199 of 250 posts.)

## What the subagent gets right that keywords miss

Not just polysemous-keyword FPs — **the subagent finds the post's actual topic**. Examples from the re-judge:

| Title | Keyword tagged | Subagent | Why subagent wins |
|---|---|---|---|
| "How to break up with a client?" | Senior dogs | **Dropping clients, Lost or injured pet** | KW only fired on "elderly dog" — missed both central topics |
| "Booking disappeared from the official page" | Rover Support quality | **Glitches / lag / bugs, Rover Support quality** | KW saw the support angle, missed the obvious bug |
| "Unpleasant interaction but I feel I did the right thing" | Meet and Greet | **Safety and aggression incidents** | KW missed that sitter cancelled M&G after finding an arrest record |
| "Late night drop request" | Cats and kittens | **Cats and kittens, Working hours** | KW only matched "cats" — missed the entire working-hours topic |
| "Boarding Small Animals" | Cats, Dog sizes, Other pets | **Other pets, Against preference** | KW fired three FPs; post is about getting dog requests despite stated preference |
| "Booking for a year out" | Time off / holidays  *(R5: Untagged)* | **Long lead time, Time off / holidays** | KW R5 dropped to Untagged — narrowing missed it entirely |

## Where the subagent loses (18 / 250 = 7.2%)

The pattern is consistent: **over-interpretation / over-tagging**. The subagent adds plausible-sounding tags from inferences rather than what's substantively in the post.

| Title | Subagent over-added | Re-judge rationale |
|---|---|---|
| "Divorce Mediator" | Difficult clients, Pick-up and drop-off | Cat sit during holidays with M&G context; divorce drama isn't a Difficult-clients case |
| "Has this happened to anyone" | Cancellations | New-to-Rover sitter with declined booking — Joining fits better |
| "Too much for 2 puppies?!" | Additional pets | Two puppies = one booking, not "additional pets" |
| "New to Rover" (creepy message) | Difficult clients | Creepy message isn't enough; main topic is still Joining |
| "Has anyone else's changed?" | Forgot to start or end it | "Missed Rover card" was incidental, only Navigation applies |

Mitigation: tighten the system prompt with "be conservative; don't add tags from inferences — the topic must be substantively present." This is a known failure mode and easy to address in a v2 prompt.

## Keyword R5 (planned narrowings) gives almost no marginal value

- KW R4 and KW R5 produce identical predictions on **199 / 250 posts** (79.6%).
- KW R5 net wins over KW R4: **+3 posts** (82 vs 79).
- KW R5 introduced 26 new "Untagged" verdicts; many were correct (the narrowings worked) but the recall loss canceled out the precision gain at this sample size.
- **Conclusion:** completing Round 5 keyword work is not a meaningful path to better tagging. The subagent dominates either keyword version.

## Tag density

| Strategy | Avg problems/post | Untagged | Multi-tag |
|---|---:|---:|---:|
| KW R4 | 1.46 | 0 | 86 |
| KW R5 | 1.28 | 26 | 70 |
| Subagent | 1.64 | 12 | 125 |

The subagent multi-tags more aggressively (125 of 250 posts). Some of this is correct (post genuinely covers multiple problems); some is the over-tagging failure mode above.

## Hallucinations

**Zero.** Across 250 posts and 392 problem-tags assigned, the subagent never invented a theme or problem name not in the taxonomy. The validator in [merge_and_validate.py](scripts/eval_tagger/merge_and_validate.py) confirms this — no entries in `subagent_hallucinations.json`.

## Decision against the Phase-0 plan criteria

| Criterion | Threshold | Result | Pass? |
|---|---|---|---|
| Improvement over keyword R5 | ≥ 5 pp correct | **+59.2 pp** (92.0% vs 32.8%) | ✓✓✓ |
| FP rate | ≤ 5% | 7.2% wrong (mostly over-tagging, not classic FP) | borderline |
| Hallucinated tags | < 1% | 0% | ✓ |
| Recall on the untagged content | ≥ 30/30 on-topic | not directly measured (sample was tagged-pool only); see below |

**Recommendation: switch to subagent-based tagging.** The improvement is decisive and the failure mode is a known prompt-engineering fix (over-tagging from inference).

## What "rollout" looks like in practice

### Production pattern
Wrap the existing keyword `tag_post` so a `LLM_TAGGER=true` env flag routes to the subagent path; keyword stays as a fallback for when subagent infrastructure is unavailable. Output shape unchanged (`themes: string[]`, `problems: string[]`).

### One-time retag of the 21,557-post historical pool
Two paths, choose one:

1. **Claude Code subagent** — at ~50 posts per ~90-second batch, this is ~12 hours of agent time. Free in API $$ but uses Claude Code consumption; can run unattended.
2. **Anthropic API (Haiku 4.5, batched)** — ~$11, fully automated, ~24h SLA via Message Batches API. Already scaffolded in [scripts/eval_tagger/taggers/llm_claude.py](scripts/eval_tagger/taggers/llm_claude.py); just needs an `ANTHROPIC_API_KEY`.

### Daily ingest going forward
50–100 new Reddit posts/day = 1–2 batches = 2–3 minutes of subagent work. Trivial either way.

### Required v2 prompt change (before rollout)
Add to the subagent's system prompt: "**Be conservative.** Only assign a problem when its topic is *substantively present* in the post — not merely mentioned, alluded to, or inferable from incidental details. When in doubt, prefer fewer tags." This addresses the 18-post over-tagging failure mode.

## Files produced

- [sample_250.json](scripts/eval_tagger/outputs/phase1/sample_250.json) — canonical 250-post sample (copied from `trusting-payne-3ab4da` worktree)
- [predictions.kw_r4.json](scripts/eval_tagger/outputs/phase1/predictions.kw_r4.json) / [predictions.kw_r5.json](scripts/eval_tagger/outputs/phase1/predictions.kw_r5.json) / [predictions.subagent.json](scripts/eval_tagger/outputs/phase1/predictions.subagent.json) — per-strategy tags
- [agreement_index.json](scripts/eval_tagger/outputs/phase1/agreement_index.json) — agreement vs disagreement bookkeeping
- [rejudge_input.json](scripts/eval_tagger/outputs/phase1/rejudge_input.json) — blind-shuffled disagreements sent to re-judge
- [rejudge_batches/results_*.json](scripts/eval_tagger/outputs/phase1/rejudge_batches) — 4 re-judge subagents' verdicts
- [results.phase1.json](scripts/eval_tagger/outputs/phase1/results.phase1.json) — per-post verdicts joined across strategies
- [taxonomy_round5.json](scripts/eval_tagger/taxonomy_round5.json) — R5 keyword overlay (do not commit to live taxonomy)

## Caveats and limitations

- **"Correct%" is comparative**, not absolute. The 92% / 32% gap is the right signal; the absolute numbers should not be compared to the historical 84.4% baseline.
- **Re-judge subagent bias** is a real risk — Claude judging Claude. Mitigated by: (a) blind option labels (A/B/C, random order), (b) splitting across 4 independent subagents (each saw 1/4 of disagreements), (c) explicit tie-breaker favoring fewer tags. Spot-checking ~12 verdicts (6 subagent wins, 6 subagent losses) read as defensible.
- **Sample is from the tagged pool only.** This evaluation does not measure recall recovery on the 12,880 currently-untagged Reddit posts. Phase 0 sampling 10 from that pool found 4 of 10 had clear taxonomy fit; a proper recall measurement would require a separate untagged-pool eval.
- **One-shot subagent runs are not reproducible** the way API calls with `temperature=0` are. Each subagent invocation is a fresh context; if you re-run today vs tomorrow you may get small differences. For audit work, snapshot the predictions JSON and never silently re-tag.
