---
description: Re-tag recent Reddit/Confluence rows in the Google Sheet using a Claude Code subagent (~92% accuracy vs ~32% for keywords). Skips rows already LLM-tagged via the `LLMTaggedAt` column; pass --force to re-process them. Run periodically to keep the dashboard in sync.
argument-hint: "[reddit|confluence|both]  [--since=Nd]  [--force]  (default: both, 7d, skip already-LLM-tagged)"
allowed-tools: Read, Write, Bash, Agent
---

# /retag-new — incremental LLM re-tag of recent rows

You are running the `/retag-new` slash command. Your job is to re-tag recently-added rows in the Google Sheet using a Claude Code subagent (the classifier validated to ~92% accuracy in `scripts/eval_tagger/outputs/phase1/summary.md`), then refresh the dashboard.

## Step 0 — Parse `$ARGUMENTS`

Default: `both --since=7d` (skips rows already LLM-tagged).

- First positional token (optional): `reddit`, `confluence`, or `both`.
- Flag: `--since=Nd` where N is an integer ≥ 1.
- Flag: `--force` — re-tag rows that already have an `LLMTaggedAt` timestamp.
  Use this when the taxonomy has changed substantively (new problem added,
  definitions reworded) and you want to re-evaluate already-tagged rows in the
  selected window. Without `--force`, those rows are skipped to avoid wasted
  work on the weekly cron.
- Anything else: abort with the valid options.

If `$ARGUMENTS` is empty, use defaults.

## Step 1 — Pre-flight

Run these checks in one Bash call:

```bash
[ -f credentials.json ] || { echo "FATAL: credentials.json not found"; exit 1; }
[ -n "$SHEET_ID" ] || { echo "Sourcing .env"; set -a && . /Users/bernardoprudencio/Documents/rover-repo/rover-sitter-monitor/.env && set +a; }
[ -n "$SHEET_ID" ] || { echo "FATAL: SHEET_ID not set even after sourcing .env"; exit 1; }
mkdir -p /tmp/retag-new && rm -f /tmp/retag-new/*
echo "OK"
```

If pre-flight fails, abort and tell the user.

## Step 2 — For each requested source, run the retag pipeline

For each source in `[reddit, confluence]` (skip the one not requested):

### 2a. Fetch rows

```bash
set -a && . /Users/bernardoprudencio/Documents/rover-repo/rover-sitter-monitor/.env && set +a
python3 scripts/retag/sheet_io.py fetch \
  --source $SOURCE \
  --since-days $N \
  $LLM_FLAG \
  --out /tmp/retag-new/${SOURCE}_input.json
```

`$LLM_FLAG` is `--only-unllm` by default (skips rows already LLM-tagged) or
`--force` if the user passed `--force` in `$ARGUMENTS`.

Read the file. If empty (`[]`), say one of:

- Default mode: "No untagged $SOURCE rows in the last $N days — skipping."
- `--force` mode: "No $SOURCE rows in the last $N days — skipping."

…and move on.

### 2b. Split into batches of 50

If 50 or fewer rows: one batch. Otherwise:

```bash
python3 - <<'PY'
import json, math
from pathlib import Path
SOURCE = "<reddit|confluence>"
rows = json.load(open(f"/tmp/retag-new/{SOURCE}_input.json"))
size = 50
n = math.ceil(len(rows) / size)
for i in range(n):
    chunk = rows[i*size:(i+1)*size]
    # Strip current_themes/current_problems so the subagent isn't biased
    clean = [{"url": r["url"], "title": r["title"], "text": r["text"]} for r in chunk]
    Path(f"/tmp/retag-new/{SOURCE}_batch_{i+1}.json").write_text(json.dumps(clean, indent=2))
print(f"{SOURCE}: split into {n} batch(es)")
PY
```

### 2c. Spawn one subagent per batch (in parallel)

For each batch file `${SOURCE}_batch_${i}.json`, spawn a `general-purpose` subagent with this prompt — pass all subagent calls **in a single message** so they run in parallel:

> You are acting as a tag classifier for r/RoverPetSitting Reddit posts and internal Rover research documents. This is a one-shot job: read the batch, tag each row against the fixed taxonomy, write results to a JSON file. Do NOT modify other files.
>
> 1. Read taxonomy: `<absolute repo path>/taxonomy.json` (107 problems, 13 themes).
> 2. Read batch: `/tmp/retag-new/<SOURCE>_batch_<i>.json` (each row has `url`, `title`, `text`).
> 3. Tag each row using ONLY problem/theme names verbatim from the taxonomy.
>    - Multi-tag is fine. "Untagged" if nothing fits.
>    - **Match topic, not vocabulary.** "I have a cat" alone ≠ Cats and kittens (cats must be substantively the topic). "navigate the neighborhood" is figurative — NOT Navigation.
>    - Include parent themes for every problem you select (deduplicated).
> 4. Write to `/tmp/retag-new/<SOURCE>_results_<i>.json` — JSON array, same order as input, format `{"url":"...","themes":["..."],"problems":["..."],"rationale":"<25 words"}`.
> 5. Validate every name exists in the taxonomy before writing.
> Return: `Wrote N tags to .../results_<i>.json. Untagged: X. Multi-tag: Y.`

Substitute the absolute repo path, `<SOURCE>`, and `<i>` per call. Use `subagent_type: general-purpose`.

### 2d. Merge & validate

```bash
python3 scripts/retag/merge_validate.py \
  --batch-glob "/tmp/retag-new/${SOURCE}_results_*.json" \
  --out /tmp/retag-new/${SOURCE}_merged.json \
  --halluc-log /tmp/retag-new/${SOURCE}_hallucinations.json
```

If hallucinations > 0, print them to the user and continue (validator already drops them).

### 2e. Write tags back to the sheet

```bash
set -a && . /Users/bernardoprudencio/Documents/rover-repo/rover-sitter-monitor/.env && set +a
python3 scripts/retag/sheet_io.py write \
  --source $SOURCE \
  --in /tmp/retag-new/${SOURCE}_merged.json
```

If this fails, **retry once** after 5 seconds. If it fails twice, stop and tell the user — the sheet may be inconsistent. Do NOT proceed to the next source or to dashboard refresh.

## Step 3 — Refresh dashboard

After all requested sources have been retagged successfully:

```bash
set -a && . /Users/bernardoprudencio/Documents/rover-repo/rover-sitter-monitor/.env && set +a
python3 rover_export_json.py --out dashboard/public/data
```

Skip if neither source had any rows to retag.

## Step 4 — Report

Tell the user:

- Per source: rows fetched / rows updated / hallucinations dropped
- Whether the dashboard was refreshed
- A reminder: "If you want to commit & push the dashboard data update, run `git add dashboard/public/data && git commit -m 'Refresh dashboard data after retag' && git push`."

Do NOT auto-commit or auto-push. The user runs the command and reviews changes themselves.

## Safety notes

- **Idempotent**: by default, re-running `/retag-new` is a no-op for already-LLM-tagged rows (the `LLMTaggedAt` column gates them out). Pass `--force` to re-evaluate them after a taxonomy change.
- **Sheet writes are batched** via `gspread.batch_update` — stays under the per-minute quota. Each row produces two batch entries (themes+problems range, then the `LLMTaggedAt` cell separately) to avoid clobbering Confluence's `Eligible`/`FilterReason` columns that sit between them.
- **Failure isolation**: a Confluence failure does not roll back Reddit changes (or vice versa); each source is committed before moving to the next.
- **No new rows are added** — `/retag-new` only updates existing rows. Use the daily GitHub Actions cron to ingest new posts; this command only rewrites tags.
