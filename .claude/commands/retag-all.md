---
description: One-time historical retag of every row in the Google Sheet using a Claude Code subagent. Resumable — uses the sheet's `LLMTaggedAt` column to skip already-done rows. Run repeatedly until done. Default 250 rows per session (~8 min). Use --limit to override; --force re-tags already-LLM-tagged rows.
argument-hint: "[reddit|confluence|both]  [--limit=N]  [--force]  (default: both, 250, skip already-LLM-tagged)"
allowed-tools: Read, Write, Bash, Agent
---

# /retag-all — resumable historical retag

You are running `/retag-all`. Same tagging pipeline as `/retag-new`, but processes ALL rows (not just recent) and tracks progress so the user can stop and resume across multiple sessions.

## Step 0 — Parse `$ARGUMENTS`

Default: `both --limit=250` (skips rows already LLM-tagged).

- First positional token (optional): `reddit`, `confluence`, or `both`.
- Flag: `--limit=N`, an integer ≥ 50 (number of rows to process this session). Default 250.
- Flag: `--force` — re-tag rows that already have an `LLMTaggedAt` timestamp.
  Use this only when the taxonomy has changed substantively (new problem
  added, definitions reworded) and you want to re-evaluate the entire pool.
  Without `--force`, the resumability of `/retag-all` depends on this flag
  being absent — runs converge as the `LLMTaggedAt` column fills in.

## Step 1 — Pre-flight

```bash
[ -f credentials.json ] || { echo "FATAL: credentials.json not found"; exit 1; }
[ -n "$SHEET_ID" ] || { set -a && . /Users/bernardoprudencio/Documents/rover-repo/rover-sitter-monitor/.env && set +a; }
[ -n "$SHEET_ID" ] || { echo "FATAL: SHEET_ID not set"; exit 1; }
mkdir -p /tmp/retag-all && rm -f /tmp/retag-all/*
echo "OK"
```

## Step 2 — For each requested source

### 2a. Fetch undone rows from the sheet

```bash
set -a && . /Users/bernardoprudencio/Documents/rover-repo/rover-sitter-monitor/.env && set +a
python3 scripts/retag/sheet_io.py fetch \
  --source $SOURCE \
  $LLM_FLAG \
  --out /tmp/retag-all/${SOURCE}_undone.json
```

`$LLM_FLAG` is `--only-unllm` by default (skips rows with a non-empty
`LLMTaggedAt`) or `--force` if the user passed `--force` in `$ARGUMENTS`.
No `--since-days` flag — this is the historical sweep.

### 2b. Slice to `--limit`

```bash
python3 - <<'PY'
import json
from pathlib import Path
SOURCE = "<reddit|confluence>"
LIMIT = <int>
rows = json.load(open(f"/tmp/retag-all/{SOURCE}_undone.json"))
slice_ = rows[:LIMIT]
Path(f"/tmp/retag-all/{SOURCE}_input.json").write_text(json.dumps(slice_, indent=2))
print(f"{SOURCE}: undone={len(rows)}, this session={len(slice_)}")
PY
```

Tell the user:

- `$SOURCE: undone rows = U, this session = min(U, $LIMIT)`

If U is 0: print `$SOURCE: ✅ all rows already LLM-tagged — skipping.` and continue to the next source.

### 2c. Split into batches of 50

```bash
python3 - <<'PY'
import json, math
from pathlib import Path
SOURCE = "<reddit|confluence>"
rows = json.load(open(f"/tmp/retag-all/{SOURCE}_input.json"))
size = 50
n = math.ceil(len(rows) / size)
for i in range(n):
    chunk = rows[i*size:(i+1)*size]
    clean = [{"url": r["url"], "title": r["title"], "text": r["text"]} for r in chunk]
    Path(f"/tmp/retag-all/{SOURCE}_batch_{i+1}.json").write_text(json.dumps(clean, indent=2))
print(f"{SOURCE}: split into {n} batch(es) of up to 50")
PY
```

### 2d. Spawn one subagent per batch IN PARALLEL

Single message containing one Agent tool-use per batch. Same prompt as `/retag-new` Step 2c, but with `/tmp/retag-all/` paths.

If a batch fails, leave its results file missing. The merge step (next) will simply skip missing batches; only successfully-tagged URLs make it into the sheet write, so only those rows get an `LLMTaggedAt` timestamp. Failed batches are picked up automatically next session.

### 2e. Merge & validate

```bash
python3 scripts/retag/merge_validate.py \
  --batch-glob "/tmp/retag-all/${SOURCE}_results_*.json" \
  --out /tmp/retag-all/${SOURCE}_merged.json \
  --halluc-log /tmp/retag-all/${SOURCE}_hallucinations.json
```

### 2f. Write tags back to the sheet

```bash
set -a && . /Users/bernardoprudencio/Documents/rover-repo/rover-sitter-monitor/.env && set +a
python3 scripts/retag/sheet_io.py write \
  --source $SOURCE \
  --in /tmp/retag-all/${SOURCE}_merged.json
```

`sheet_io.py write` writes themes, problems, AND the `LLMTaggedAt` timestamp
in the same `batch_update` call. So when the write succeeds, progress is
durably recorded in the sheet itself — the next `/retag-all` invocation will
skip these URLs automatically via `--only-unllm`.

**Retry once after 5s on failure.** If it fails twice, abort that source —
the rows will still show empty `LLMTaggedAt` cells, so the next session
naturally retries them. Tell the user.

## Step 3 — Refresh dashboard

After all requested sources are done (or skipped):

```bash
set -a && . /Users/bernardoprudencio/Documents/rover-repo/rover-sitter-monitor/.env && set +a
python3 rover_export_json.py --out dashboard/public/data
```

## Step 4 — Report

Per source, print:

- `$SOURCE: this session updated N rows; R remaining undone (~⌈R/250⌉ more sessions at the default limit).`

(R is the post-write count of rows with empty `LLMTaggedAt` — re-fetch with
`--only-unllm` to compute it, or just subtract: `R = pre-session-undone - N`.)

End with a reminder: "Run `/retag-all` again to continue. To commit dashboard updates, run `git add dashboard/public/data && git commit && git push`."

## Notes

- **Source of truth for progress**: the sheet's `LLMTaggedAt` column. Empty cell = needs LLM tag; non-empty = already done. `--only-unllm` (the default) skips the latter, so re-running `/retag-all` is idempotent and resumable across sessions and machines.
- **Failure mode**: if a batch's subagent times out or returns malformed JSON, those rows never get an `LLMTaggedAt` timestamp written — they're picked up on the next session automatically.
- **Confluence is small** (~70 rows): one session almost certainly finishes it.
- **Reddit is big** (21,557 rows ≈ 86 sessions at default 250). To go faster in one sitting, pass `--limit=500` or higher; the parallelism is per-batch (50 each), so 1000 = 20 batches in parallel — be aware of subagent quota / API rate.
- **Reset**: to re-tag the whole pool from scratch (e.g., after a major taxonomy change), run with `--force`. There is no separate "reset" step.
