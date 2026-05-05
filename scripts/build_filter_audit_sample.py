"""Build a 50 included + 50 excluded audit sample for the Confluence filter.

Reads the live 'Confluence Research' sheet, partitions rows by Eligible
column, samples uniformly with seed 20260505 (same seed used across all
audits), writes JSON to reviews/<date>-confluence-filter-round1-input/sample_100.json.

Run from the project root:
    set -a && . .env && set +a
    python3 scripts/build_filter_audit_sample.py
"""
from __future__ import annotations

import json
import os
import random
import sys
from datetime import date, datetime, timezone

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from rover_confluence_dump import get_sheet, get_research_ws, WORKSHEET_NAME

SEED = 20260505
PER_BUCKET = 50


def main() -> None:
    print("Connecting to Google Sheets...")
    sheet = get_sheet()
    ws = get_research_ws(sheet)

    rows = ws.get_all_values()
    if len(rows) < 2:
        print("  Sheet is empty.")
        return

    header = rows[0]
    data = rows[1:]
    idx = {name: i for i, name in enumerate(header)}

    def col(row, name, default=""):
        i = idx.get(name)
        if i is None or i >= len(row):
            return default
        return row[i] or default

    eligible_rows = [r for r in data if col(r, "Eligible").lower() == "yes"]
    excluded_rows = [r for r in data if col(r, "Eligible").lower() == "no"]
    print(f"  Total: {len(data)} rows. Eligible: {len(eligible_rows)}. Excluded: {len(excluded_rows)}.")

    rng = random.Random(SEED)
    inc_n = min(PER_BUCKET, len(eligible_rows))
    exc_n = min(PER_BUCKET, len(excluded_rows))
    inc_sample = rng.sample(eligible_rows, inc_n)
    exc_sample = rng.sample(excluded_rows, exc_n)

    def to_record(r, bucket):
        return {
            "bucket": bucket,
            "id": col(r, "PageID"),
            "space": col(r, "Space"),
            "title": col(r, "Title"),
            "url": col(r, "URL"),
            "author": col(r, "Author"),
            "labels": [l.strip() for l in col(r, "Labels").split(",") if l.strip()],
            "themes": [t.strip() for t in col(r, "Themes").split(",") if t.strip()],
            "problems": [p.strip() for p in col(r, "Problems").split(",") if p.strip()],
            "excerpt": col(r, "Excerpt"),
            "eligible": col(r, "Eligible"),
            "filter_reason": col(r, "FilterReason"),
        }

    sample = (
        [to_record(r, "included") for r in inc_sample]
        + [to_record(r, "excluded") for r in exc_sample]
    )

    today = date.today().isoformat()
    out_dir = os.path.join("reviews", f"{today}-confluence-filter-round1-input")
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "sample_100.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(
            {
                "generated_at_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
                "seed": SEED,
                "total_rows": len(data),
                "eligible_total": len(eligible_rows),
                "excluded_total": len(excluded_rows),
                "included_sampled": inc_n,
                "excluded_sampled": exc_n,
                "sample": sample,
            },
            f,
            ensure_ascii=False,
            indent=2,
        )
    print(f"  ✅ Wrote {out_path} ({len(sample)} rows)")


if __name__ == "__main__":
    main()
