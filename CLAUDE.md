# Rover Sitter Monitor — Project Notes

Two ingestion pipelines feeding one taxonomy and one dashboard:

- **Reddit** (daily): r/RoverPetSitting → Google Sheets ("Reddit Posts" tab) → `tag_post`.
- **Confluence** (weekly): internal research from spaces DSN + PSD → Google Sheets ("Confluence Research" tab) → same `tag_post`.

Both surfaces consume `taxonomy.json` (the single source of truth) and render on the same dashboard, with research linked alongside Reddit on each problem/theme page. Tag quality is iteratively audited round-by-round.

## Current state (as of 2026-05-05, Round 4)

- **Tagged-pool size:** 8,453 / 21,557 posts (Round 4 retag, post-FP-cleanup)
- **Audit accuracy:** **84.4% correct**, 10.4% FP, Wilson 95% CI 79.4–88.4%
- **Trajectory:** baseline 83.6% → Round 3 57.2% (recall expansion over-corrected) → **Round 4 84.4%** (FP cleanup recovered)

## Tagging method (as of 2026-05-06)

The keyword tagger in [rover_sheet_dump.py:48](rover_sheet_dump.py:48) is the **fallback** baseline — used by the daily GitHub Actions cron when ingesting new posts. The **primary** tagger is now a Claude Code subagent, validated to ~92% accuracy vs ~32% for keyword R4 in [scripts/eval_tagger/outputs/phase1/summary.md](scripts/eval_tagger/outputs/phase1/summary.md). To bring the sheet up to subagent quality, run one of these slash commands periodically from a Claude Code session in this repo:

- **`/retag-new [reddit|confluence|both] [--since=Nd] [--force]`** — re-tag recent rows (default 7d, both sources). Skips rows already LLM-tagged via the `LLMTaggedAt` column; pass `--force` to re-evaluate them after a taxonomy change. Run weekly-ish to keep the dashboard current.
- **`/retag-all [reddit|confluence|both] [--limit=N] [--force]`** — resumable historical retag of every row. Progress is tracked durably in the sheet's `LLMTaggedAt` column (col I for Reddit, col M for Confluence) — empty cell = needs LLM tag. Run repeatedly until no rows remain undone. Default 250 rows/session (~8 min).

Both commands: read sheet (skipping LLM-tagged rows by default) → spawn subagent(s) in parallel → validate against taxonomy whitelist → batch-update Themes/Problems AND `LLMTaggedAt` columns → refresh dashboard JSON. They do NOT auto-commit dashboard data — review and push manually when satisfied.

The Round-5 keyword work is **deprioritized** — Phase 1 evaluation showed only +3/250 net wins over Round 4. Polishing keywords beyond R4 has near-zero ROI now that the subagent path is live.

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

## Confluence pipeline

- **Spaces:** `DSN` (User Experience) + `PSD` (Provider Space). Override with the `CONFLUENCE_SPACE_KEYS` env var (comma-separated keys).
- **Cadence:** weekly cron (Mondays 08:00 UTC) in [.github/workflows/daily_digest.yml](.github/workflows/daily_digest.yml). Daily cron skips this job — research lands too slowly to merit daily fetch.
- **Auth env vars:** `CONFLUENCE_DOMAIN` (`roverdotcom.atlassian.net`), `CONFLUENCE_EMAIL`, `CONFLUENCE_API_TOKEN`. Generate token at https://id.atlassian.com/manage-profile/security/api-tokens.
- **Cursor:** `confluence_meta` worksheet stores `last_run_utc`. Subsequent runs only fetch pages with `version.createdAt > cursor`. Use `--full` to ignore the cursor and re-fetch everything.
- **Tagging:** uses the same `tag_post` from [rover_sheet_dump.py:48](rover_sheet_dump.py:48) — research is regex-tagged with the same keyword list as Reddit. Long-form research uses formal language and may have lower recall than Reddit.
- **Eligibility filter:** `evaluate_eligibility` in [rover_confluence_dump.py](rover_confluence_dump.py) gates which pages reach the dashboard. Two AND'd checks: (1) doc-type is a finding (title whitelist + label/title blocklist), (2) audience is provider-relevant (PSD admits by default; DSN requires sitter/walker/trainer/groomer/provider/host/etc. terms in title or body). Verdict is stored on every row in columns `Eligible` (yes/no) and `FilterReason` (e.g. `non_findings_title:script`, `non_provider:dsn_no_provider_terms`). The dashboard skips rows where `Eligible="no"`. Rule derivation: [reviews/2026-05-05-confluence-filter-rules-derivation.md](reviews/2026-05-05-confluence-filter-rules-derivation.md). Audit accuracy is tracked round-by-round in `reviews/<date>-confluence-filter-roundN.md`.
- **Sheet schema (12 cols):** `PageID | Updated | Space | Title | URL | Author | Excerpt | Themes | Problems | Labels | Eligible | FilterReason`. Pre-filter sheets had 10 cols; `--retag` extends them to 12 idempotently.
- **`--retag` mode:** `python3 rover_confluence_dump.py --retag` re-runs both `tag_post` AND `evaluate_eligibility` on stored rows in place, no Confluence fetch. Run after each taxonomy round AND after each filter round.
- **`--inspect` mode:** read-only snapshot of the sheet (label / title / author distributions + a 75-row random sample at seed `20260505`) into `reviews/<date>-confluence-discovery.{md,json}`. Used to design or revise the filter from real data.
- **`--no-filter` mode:** bypass the eligibility filter (every row written with `Eligible="yes"`, `FilterReason="bypassed"`). For debug dumps and audit baselines only — do not deploy.
- **Make targets:** `make confluence-dump` / `make confluence-retag` / `make confluence-full`.

## Operational nuance

- **Auth:** `credentials.json` must be in CWD (this worktree has it as a symlink to the main repo's file; gitignored). `SHEET_ID` env var comes from `.env` at the repo root.
- **Sheet writes:** `--retag` modifies the live Google Sheet. Confirm with the user before running; idempotent but it's shared state.
- **PREVIEW_MAX:** raised from 200 → 500 in [rover_export_json.py:24](rover_export_json.py:24) during Round 4. The dashboard preview now matches what `tag_post` sees, so audit findings are interpretable without opening Reddit URLs.
- **Sample seed `20260505`** is fixed across rounds for comparability. Don't change it.
- **`trust and safety` dual-fire** — deliberately in both `Safety and aggression incidents` and `Rover Support quality`. User aware; revisit if it gets noisy.

## Files

- [taxonomy.json](taxonomy.json) — 107 problems × 13 themes, single source of truth
- [rover_sheet_dump.py](rover_sheet_dump.py) — Reddit ingest, `tag_post` matcher (line 48), `--retag` mode (line 263)
- [rover_confluence_dump.py](rover_confluence_dump.py) — Confluence ingest, reuses `tag_post`, holds `evaluate_eligibility` filter, `--retag` / `--full` / `--limit` / `--space` / `--inspect` / `--no-filter` flags
- [rover_export_json.py](rover_export_json.py) — sheet → dashboard JSON for both Reddit and Confluence, `PREVIEW_MAX` (line 24); skips Confluence rows where `Eligible="no"`
- [tests/test_taxonomy.py](tests/test_taxonomy.py) — 3 smoke tests; must pass after every taxonomy edit
- [tests/test_confluence_filter.py](tests/test_confluence_filter.py) — 22 unit tests for `evaluate_eligibility`; must pass after every filter rule edit
- `reviews/` — per-round markdown + JSON sidecar audits; each round links forward via "Round N+1 plan" section
