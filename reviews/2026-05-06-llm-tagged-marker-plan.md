# LLM Tagged Marker — Implementation Plan

**Date:** 2026-05-06
**Status:** Ready to execute. All steps are sequential; pause at auth checkpoints.

## Context for fresh sessions

Before starting, read these in order:

1. This file (you're here).
2. [scripts/eval_tagger/outputs/phase1/summary.md](scripts/eval_tagger/outputs/phase1/summary.md) — why subagent tagging beats keyword (92% vs ~32%); the *why* behind everything below.
3. [CLAUDE.md](CLAUDE.md) — project conventions; specifically the "**Sheet writes**: confirm with the user before running" rule.
4. [scripts/retag/sheet_io.py](scripts/retag/sheet_io.py) — current implementation you'll modify in Step 2.
5. [.claude/commands/retag-new.md](.claude/commands/retag-new.md) and [.claude/commands/retag-all.md](.claude/commands/retag-all.md) — current slash commands you'll modify in Step 3.

## What's already done

- **Phase 1 evaluation:** subagent (Claude Code agent) tagging beats keyword R4/R5 by **+59pp** on the 250-post audit (92% vs 32-33%). Zero hallucinations. Full report in [scripts/eval_tagger/outputs/phase1/summary.md](scripts/eval_tagger/outputs/phase1/summary.md).
- **Decided against:** Cowork (user can't easily set it up), Anthropic API key (no provisioning).
- **Decided for:** manual slash commands run from a Claude Code session in this repo, periodically.
- **Built but not yet shipped:**
  - [scripts/retag/sheet_io.py](scripts/retag/sheet_io.py) — sheet read/write helpers
  - [scripts/retag/merge_validate.py](scripts/retag/merge_validate.py) — taxonomy validator + batch merger
  - [scripts/retag/progress.py](scripts/retag/progress.py) — local progress tracking (will be **deleted** in this plan)
  - [scripts/retag/subagent_prompt.md](scripts/retag/subagent_prompt.md) — validated v1 prompt template
  - [.claude/commands/retag-new.md](.claude/commands/retag-new.md) — `/retag-new`
  - [.claude/commands/retag-all.md](.claude/commands/retag-all.md) — `/retag-all`
- **CLAUDE.md** updated to reflect that subagent tagging is the primary path; Round 5 keyword work is deprioritized.
- **Smoke test (read-only) passed** end-to-end on 1 row. Sheet write was correctly blocked pending explicit user authorization.

## Why this plan exists

The current `/retag-{new,all}` commands have no way to know whether a row was already subagent-tagged. Without a marker:

- `/retag-new --since=7d` re-processes the same rows every weekly run (wasted work).
- `/retag-all` would never converge unless we use the now-obsolete `progress.py` local file, which is brittle (lost if you `rm` it) and tied to one machine.

**Decision (2026-05-06):** add an `LLMTaggedAt` column to each sheet as a durable, queryable marker. Empty cell = never LLM-tagged. ISO timestamp = LLM-tagged at that moment. The sheet itself becomes the source of truth.

The user explicitly approved this approach. Proceed.

## Steps

### Step 1 — Migration script (one-time, writes 2 cells)

Create [scripts/retag/migrate_add_marker_column.py](scripts/retag/migrate_add_marker_column.py). It:

- Authenticates via `SHEET_ID` env var + `credentials.json`.
- Writes `LLMTaggedAt` to:
  - **Reddit Posts** cell `I1`
  - **Confluence Research** cell `M1`
- Bolds the header cell (formatting consistency with existing headers).
- **Idempotent** — read the cell first; skip if it already says `LLMTaggedAt`. Print "already migrated" in that case.

**🔒 Auth checkpoint #1:** This is a sheet write. Tell the user exactly what cells will change ("`Reddit Posts!I1` and `Confluence Research!M1` to `LLMTaggedAt`"). Wait for explicit confirmation before running.

After confirmation:

```bash
set -a && . /Users/bernardoprudencio/Documents/rover-repo/rover-sitter-monitor/.env && set +a
python3 scripts/retag/migrate_add_marker_column.py
```

### Step 2 — Update [scripts/retag/sheet_io.py](scripts/retag/sheet_io.py)

Edit in place:

- **Schemas:** add `"llm_tagged_col": "I"` to `reddit`; `"llm_tagged_col": "M"` to `confluence`.
- **`Row` dataclass:** add `llm_tagged_at: str` field. `fetch_rows` populates it from the new column.
- **`fetch_rows()`:** add kwarg `only_unllm: bool = True`. When True, skip rows where `llm_tagged_at.strip()` is non-empty.
- **`write_tags()`:** write the ISO timestamp too. Currently the batch range is `{themes_col}{row}:{problems_col}{row}` (2 cells). Change to `{themes_col}{row}:{llm_tagged_col}{row}` (3 cells, columns F–I for Reddit / H–M for Confluence). Wait — for Confluence, columns H–M is 6 cells, with K (Eligible) and L (FilterReason) in between. Don't overwrite those. **Use a separate batch entry for the timestamp cell** to avoid clobbering Eligible/FilterReason. Two entries per row in the `batch_update` payload: one for `{themes_col}{row}:{problems_col}{row}` (themes+problems), one for `{llm_tagged_col}{row}` (timestamp). For Reddit they could be merged but consistency wins.
- **CLI:** `fetch` subcommand gains `--only-unllm` / `--force` flag (mutually exclusive). Default is `--only-unllm`.

### Step 3 — Update slash commands

**[.claude/commands/retag-new.md](.claude/commands/retag-new.md):**
- Step 0: parse a `--force` flag from `$ARGUMENTS`.
- Step 2a: pass `--only-unllm` (the default) unless `--force` was given, in which case pass `--force`.
- Update `argument-hint` and `description` frontmatter to mention `[--force]`.

**[.claude/commands/retag-all.md](.claude/commands/retag-all.md):**
- Replace the `progress.py filter-undone` invocation in Step 2b with: `sheet_io.py fetch --source $SOURCE --only-unllm --out ...` followed by a small Python slice to take the first `--limit` rows.
- Drop the `progress.py mark-done` call in Step 2g (the sheet's `LLMTaggedAt` column is now the persistent record).
- Add `--force` flag handling, same shape as `/retag-new`.
- Update argument-hint and description.

### Step 4 — Delete obsolete file

```bash
rm scripts/retag/progress.py
```

If a `progress.json` exists from prior testing: `rm scripts/retag/progress.json` too. (It's gitignored already.)

### Step 5 — Live smoke test (one row)

Goal: validate the full pipeline including the sheet write and the `LLMTaggedAt` filter.

1. Fetch with default filter:
   ```bash
   set -a && . /Users/bernardoprudencio/Documents/rover-repo/rover-sitter-monitor/.env && set +a
   python3 scripts/retag/sheet_io.py fetch --source reddit --since-days 1 --only-unllm --out /tmp/smoke_in.json
   ```
2. Expect 1 row (the "Going out to dinner during a house sit - appropriate?" row, currently keyword-Untagged, no `LLMTaggedAt`). If 0 rows, no fresh untagged content today — pick `--since-days 7` and take the first row instead.
3. Spawn 1 subagent on that row using the prompt template from [scripts/retag/subagent_prompt.md](scripts/retag/subagent_prompt.md). Output to `/tmp/smoke_results.json`.
4. Merge + validate:
   ```bash
   python3 scripts/retag/merge_validate.py --batch-glob "/tmp/smoke_results*.json" --out /tmp/smoke_merged.json
   ```
5. Show the user the proposed tags. **🔒 Auth checkpoint #2:** confirm before writing to the sheet.
6. After confirmation:
   ```bash
   python3 scripts/retag/sheet_io.py write --source reddit --in /tmp/smoke_merged.json
   ```
7. Re-fetch the same row to verify both updates landed:
   ```bash
   python3 scripts/retag/sheet_io.py fetch --source reddit --since-days 1 --out /tmp/smoke_verify.json
   ```
   Expect: themes/problems are the new values, `llm_tagged_at` is a recent ISO timestamp (sometime in the last few minutes).
8. Re-run with the default filter (which now skips LLM-tagged rows):
   ```bash
   python3 scripts/retag/sheet_io.py fetch --source reddit --since-days 1 --only-unllm --out /tmp/smoke_filter.json
   ```
   Expect 0 rows. Confirms the marker correctly excludes already-tagged rows.

If any of those expectations fail, stop and diagnose before declaring success.

### Step 6 — Ship

When the smoke test passes:

- `git status` to see all the changes
- Show diff to user, get OK
- Commit with a clear message (e.g., `Add LLMTaggedAt marker column for subagent retag pipeline`)
- Push

Then the user can run `/retag-all reddit` to begin the historical retag (~86 sessions × ~8 min at default `--limit=250`, or fewer sessions at higher `--limit`).

## Operational nuance

- **credentials.json:** this worktree should have a symlink to the parent repo's file. If not, run:
  ```bash
  ln -s /Users/bernardoprudencio/Documents/rover-repo/rover-sitter-monitor/credentials.json credentials.json
  ```
- **SHEET_ID:** source from .env:
  ```bash
  set -a && . /Users/bernardoprudencio/Documents/rover-repo/rover-sitter-monitor/.env && set +a
  ```
- **GH Actions daily cron append behavior:** writes 8 cols (Reddit) / 12 cols (Confluence) per row. Adding col I / M for the marker **does not** break appends — newly fetched rows simply leave the `LLMTaggedAt` cell empty, which is exactly what `--only-unllm` will pick up next time `/retag-new` runs. **No GH Actions workflow changes needed.**
- **`--force` semantics:** intended for the case where the taxonomy changes substantively (e.g., new problem added, definitions reworded) and you want to re-evaluate already-tagged rows. Document this in the slash-command markdown so future-you remembers.

## Out of scope for this plan (don't get distracted)

- Improving the subagent prompt (v2 attempt was a wash — see Phase 1 summary).
- Building Confluence-specific tagging logic (the v1 prompt handles both fine).
- Migrating to Anthropic API ($11 batched alternative). Revisit only if subagent runs become impractical.
- Touching the GH Actions workflow.
