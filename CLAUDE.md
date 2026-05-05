# Rover Sitter Monitor — Project Notes

Reddit r/RoverPetSitting → Google Sheets pipeline + tagging taxonomy + dashboard. Iteratively auditing tag quality round-by-round.

## Current state (as of 2026-05-05, Round 4)

- **Tagged-pool size:** 8,453 / 21,557 posts (Round 4 retag, post-FP-cleanup)
- **Audit accuracy:** **84.4% correct**, 10.4% FP, Wilson 95% CI 79.4–88.4%
- **Trajectory:** baseline 83.6% → Round 3 57.2% (recall expansion over-corrected) → **Round 4 84.4%** (FP cleanup recovered)

## What to do next: Round 5

Full plan with concrete keyword recipes lives in [reviews/2026-05-05-tag-review-round4.md](reviews/2026-05-05-tag-review-round4.md), starting at "Round 5 plan" (~line 138). Read that file first.

Headline targets: `correct ≥ 88%`, FP rate ≤ 6%.

Priority levers (all FP cleanup, no recall expansion):

1. **`cat` / `cats` cluster** — 7 of 26 FPs (incl. `cat scan` medical). Drop bare `cat`, keep `cats`/`kitten`/`feline`, add specific phrases (`cat sitter`, `cat boarding`, `kitty`, etc).
2. **`training`** in High quality pet care — 3 FPs. Replace with `sitter training`, `training certification`, `dog trainer` (sitter-as-trainer).
3. **`breed`** in Breeds — 3 FPs. Replace with `breed restriction`, `dog breed`, `breed concern`, `breed ban`.
4. **`unavailable`** — 2 FPs. Replace with `mark unavailable`, `set unavailable`, `i'm unavailable`.
5. **`more clients`, `navigate`, `can't find`** — 2 FPs each. See review for replacements.
6. **Spot-check Reminders + Trial recall** — Round 4 narrowing produced zero firings in the sample. Sample 50 untagged posts and check whether topic is genuinely rare or whitelist is too strict.

## How to run a round

```bash
# 1. Edit taxonomy.json (and/or rover_export_json.py if changing PREVIEW_MAX)
# 2. Run tests
python3 -m pytest tests/test_taxonomy.py -v

# 3. Source env + retag the sheet
set -a && . /Users/bernardoprudencio/Documents/rover-repo/rover-sitter-monitor/.env && set +a
python3 rover_sheet_dump.py --retag       # rewrites sheet Themes/Problems columns
make export                                # refresh dashboard JSON (new posts.<hash>.json)

# 4. Sample 250 posts uniformly with seed 20260505 (same seed every round) into reviews/round{N}_input/sample_250.json
# 5. Spawn a general-purpose subagent with the audit protocol from Round 4
#    (see reviews/2026-05-05-tag-review-round4.md for the exact prompt structure)
# 6. Subagent writes reviews/<date>-tag-review-round{N}.{md,json}
```

## Operational nuance

- **Auth:** `credentials.json` must be in CWD (this worktree has it as a symlink to the main repo's file; gitignored). `SHEET_ID` env var comes from `.env` at the repo root.
- **Sheet writes:** `--retag` modifies the live Google Sheet. Confirm with the user before running; idempotent but it's shared state.
- **PREVIEW_MAX:** raised from 200 → 500 in [rover_export_json.py:24](rover_export_json.py:24) during Round 4. The dashboard preview now matches what `tag_post` sees, so audit findings are interpretable without opening Reddit URLs.
- **Sample seed `20260505`** is fixed across rounds for comparability. Don't change it.
- **`trust and safety` dual-fire** — deliberately in both `Safety and aggression incidents` and `Rover Support quality`. User aware; revisit if it gets noisy.

## Files

- [taxonomy.json](taxonomy.json) — 107 problems × 13 themes, single source of truth
- [rover_sheet_dump.py](rover_sheet_dump.py) — `tag_post` matcher (line 48), `--retag` mode (line 263)
- [rover_export_json.py](rover_export_json.py) — sheet → dashboard JSON, `PREVIEW_MAX` (line 24)
- [tests/test_taxonomy.py](tests/test_taxonomy.py) — 3 smoke tests; must pass after every taxonomy edit
- `reviews/` — per-round markdown + JSON sidecar audits; each round links forward via "Round N+1 plan" section
