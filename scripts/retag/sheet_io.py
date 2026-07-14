"""Sheet I/O helpers for the LLM retag workflow.

Reads from and writes to the same Google Sheet that rover_sheet_dump.py uses.
Two worksheets supported:
  - "Reddit Posts"  — cols: Date | Title | URL | Author | Preview | Themes | Problems | Subreddit | LLMTaggedAt
  - "Confluence Research" — cols: PageID | Updated | Space | Title | URL | Author | Excerpt | Themes | Problems | Labels | Eligible | FilterReason | LLMTaggedAt

The retag workflow never adds new rows; it only updates the Themes/Problems
and LLMTaggedAt cells for existing rows. The LLMTaggedAt cell is empty when a
row has never been LLM-tagged and holds an ISO-8601 UTC timestamp once it has
— this is the durable marker that lets `--only-unllm` skip already-processed
rows across runs and machines.
"""
from __future__ import annotations

import os
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Iterable

import gspread
from google.oauth2.service_account import Credentials

SHEET_ID = os.environ.get("SHEET_ID")
CREDS_FILE = os.environ.get("CREDS_FILE", "credentials.json")

# Worksheet schemas — (worksheet_name, text_field_col_letter, themes_col_letter, problems_col_letter)
SCHEMAS = {
    "reddit": {
        "worksheet": "Reddit Posts",
        "title_col": "B",         # 2
        "url_col": "C",           # 3
        "text_col": "E",          # 5 — Preview
        "themes_col": "F",        # 6
        "problems_col": "G",      # 7
        "date_col": "A",          # 1 — "YYYY-MM-DD HH:MM UTC"
        "llm_tagged_col": "I",    # 9 — ISO timestamp; empty = never LLM-tagged
    },
    "confluence": {
        "worksheet": "Confluence Research",
        "title_col": "D",         # 4
        "url_col": "E",           # 5
        "text_col": "G",          # 7 — Excerpt
        "themes_col": "H",        # 8
        "problems_col": "I",      # 9
        "date_col": "B",          # 2 — "YYYY-MM-DDTHH:MM:SSZ"
        "eligible_col": "K",      # 11 — "yes"/"no"; only retag rows where eligible == "yes"
        "llm_tagged_col": "M",    # 13 — ISO timestamp; empty = never LLM-tagged
    },
}


@dataclass
class Row:
    row_num: int          # 1-based, including header (so first data row = 2)
    url: str
    title: str
    text: str             # preview / excerpt — input to the tagger
    current_themes: str   # comma-separated as stored in sheet
    current_problems: str
    date: str             # raw date string from the sheet
    llm_tagged_at: str    # ISO timestamp; empty string = never LLM-tagged


def _open_worksheet(name: str):
    if not SHEET_ID:
        raise SystemExit("FATAL: SHEET_ID env var not set. Source .env first.")
    if not os.path.exists(CREDS_FILE):
        raise SystemExit(f"FATAL: {CREDS_FILE} not found in {os.getcwd()}")
    scopes = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive",
    ]
    creds = Credentials.from_service_account_file(CREDS_FILE, scopes=scopes)
    client = gspread.authorize(creds)
    return client.open_by_key(SHEET_ID).worksheet(name)


def _parse_date(source: str, raw: str) -> datetime | None:
    if not raw:
        return None
    try:
        if source == "reddit":
            return datetime.strptime(raw, "%Y-%m-%d %H:%M UTC").replace(tzinfo=timezone.utc)
        # confluence — ISO 8601 with Z
        return datetime.fromisoformat(raw.replace("Z", "+00:00"))
    except (ValueError, TypeError):
        return None


def _col_idx(letter: str) -> int:
    """A->0, B->1, ..."""
    return ord(letter.upper()) - ord("A")


def fetch_rows(source: str,
               since_days: int | None = None,
               since_dt: datetime | None = None,
               only_untagged: bool = False,
               only_unllm: bool = True) -> list[Row]:
    """Read rows from the sheet, applying optional filters.

    Args:
      source: 'reddit' or 'confluence'
      since_days: only return rows with date within the last N days
      since_dt: alternative to since_days — explicit cutoff datetime
      only_untagged: only return rows where current themes/problems == "Untagged"
                     (useful for "retag everything keyword left untagged")
      only_unllm: only return rows where the LLMTaggedAt cell is empty
                  (i.e., never been LLM-tagged). Default True. Pass False to
                  re-evaluate already-LLM-tagged rows (e.g., after a taxonomy
                  change).

    Confluence: rows where Eligible != "yes" are silently filtered out
    (matches dashboard behavior).
    """
    if source not in SCHEMAS:
        raise ValueError(f"Unknown source: {source}")
    schema = SCHEMAS[source]
    ws = _open_worksheet(schema["worksheet"])
    all_rows = ws.get_all_values()
    if not all_rows or len(all_rows) < 2:
        return []

    cutoff = since_dt
    if cutoff is None and since_days is not None:
        cutoff = datetime.now(timezone.utc) - timedelta(days=since_days)

    title_i = _col_idx(schema["title_col"])
    url_i = _col_idx(schema["url_col"])
    text_i = _col_idx(schema["text_col"])
    themes_i = _col_idx(schema["themes_col"])
    problems_i = _col_idx(schema["problems_col"])
    date_i = _col_idx(schema["date_col"])
    eligible_i = _col_idx(schema["eligible_col"]) if "eligible_col" in schema else None
    llm_tagged_i = _col_idx(schema["llm_tagged_col"])

    out: list[Row] = []
    for i, row in enumerate(all_rows[1:], start=2):  # row_num is 1-based, +1 for header
        def cell(idx: int) -> str:
            return row[idx] if len(row) > idx else ""

        if eligible_i is not None and cell(eligible_i).strip().lower() != "yes":
            continue

        llm_tagged_at = cell(llm_tagged_i)
        if only_unllm and llm_tagged_at.strip():
            continue

        date_str = cell(date_i)
        if cutoff is not None:
            dt = _parse_date(source, date_str)
            if dt is None or dt < cutoff:
                continue

        themes_str = cell(themes_i)
        problems_str = cell(problems_i)
        if only_untagged and themes_str != "Untagged" and problems_str != "Untagged":
            continue

        url = cell(url_i)
        if not url:
            continue
        out.append(Row(
            row_num=i,
            url=url,
            title=cell(title_i),
            text=cell(text_i),
            current_themes=themes_str,
            current_problems=problems_str,
            date=date_str,
            llm_tagged_at=llm_tagged_at,
        ))
    return out


def write_tags(source: str, tags_by_url: dict[str, dict]) -> int:
    """Write {themes, problems} back to rows keyed by URL.

    Args:
      source: 'reddit' or 'confluence'
      tags_by_url: {url: {"themes": [...], "problems": [...]}}

    Returns the number of rows updated.
    """
    if source not in SCHEMAS:
        raise ValueError(f"Unknown source: {source}")
    schema = SCHEMAS[source]
    ws = _open_worksheet(schema["worksheet"])
    all_rows = ws.get_all_values()
    if not all_rows or len(all_rows) < 2:
        return 0

    url_i = _col_idx(schema["url_col"])

    # Build URL -> all matching row_nums (a URL can appear in duplicate rows)
    url_to_rows: dict[str, list[int]] = {}
    for i, row in enumerate(all_rows[1:], start=2):
        u = row[url_i] if len(row) > url_i else ""
        if u:
            url_to_rows.setdefault(u, []).append(i)

    now_iso = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    updates = []
    skipped_urls = []
    rows_updated = 0
    for url, tags in tags_by_url.items():
        row_nums = url_to_rows.get(url)
        if not row_nums:
            skipped_urls.append(url)
            continue
        themes_str = ", ".join(tags.get("themes", []) or ["Untagged"])
        problems_str = ", ".join(tags.get("problems", []) or ["Untagged"])
        for row_num in row_nums:
            # Two batch entries per row: themes+problems together, then the LLMTaggedAt
            # cell separately. Confluence has Eligible/FilterReason between Problems (I)
            # and LLMTaggedAt (M); writing as one range would clobber them.
            updates.append({
                "range": f"{schema['themes_col']}{row_num}:{schema['problems_col']}{row_num}",
                "values": [[themes_str, problems_str]],
            })
            updates.append({
                "range": f"{schema['llm_tagged_col']}{row_num}",
                "values": [[now_iso]],
            })
            rows_updated += 1

    if skipped_urls:
        print(f"WARNING: {len(skipped_urls)} URLs not found in sheet — skipped (first 3: {skipped_urls[:3]})")

    if not updates:
        return 0
    ws.batch_update(updates, value_input_option="RAW")
    return rows_updated


# ──────────────── CLI ────────────────

def _main_cli():
    """CLI entry point — used by the slash command via Bash.

    Subcommands:
      fetch  --source SOURCE [--since-days N] [--only-untagged] [--only-unllm|--force] --out PATH
        Writes JSON [{row_num, url, title, text, ...}, ...] for the subagent to consume.
        Default behavior skips rows already LLM-tagged; pass --force to include them.
      write  --source SOURCE --in PATH
        Reads JSON [{url, themes, problems}, ...] and writes back to the sheet
        (themes, problems, and LLMTaggedAt timestamp).
    """
    import argparse
    import json
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)

    fp = sub.add_parser("fetch")
    fp.add_argument("--source", required=True, choices=["reddit", "confluence"])
    fp.add_argument("--since-days", type=int, default=None)
    fp.add_argument("--only-untagged", action="store_true")
    fp.add_argument("--out", required=True)
    llm_group = fp.add_mutually_exclusive_group()
    llm_group.add_argument(
        "--only-unllm", dest="only_unllm", action="store_true", default=True,
        help="Skip rows already LLM-tagged (default).",
    )
    llm_group.add_argument(
        "--force", dest="only_unllm", action="store_false",
        help="Include rows already LLM-tagged (use after taxonomy changes).",
    )

    wp = sub.add_parser("write")
    wp.add_argument("--source", required=True, choices=["reddit", "confluence"])
    wp.add_argument("--in", dest="in_path", required=True)

    args = ap.parse_args()

    if args.cmd == "fetch":
        rows = fetch_rows(
            args.source,
            since_days=args.since_days,
            only_untagged=args.only_untagged,
            only_unllm=args.only_unllm,
        )
        # Strip Row to a JSON-safe shape for the subagent (it doesn't need row_num)
        payload = [
            {
                "row_num": r.row_num,
                "url": r.url,
                "title": r.title,
                "text": r.text,
                "current_themes": r.current_themes,
                "current_problems": r.current_problems,
                "llm_tagged_at": r.llm_tagged_at,
            }
            for r in rows
        ]
        with open(args.out, "w") as f:
            json.dump(payload, f, indent=2)
        print(f"Wrote {len(payload)} rows to {args.out}")
    elif args.cmd == "write":
        with open(args.in_path) as f:
            results = json.load(f)
        tags_by_url = {r["url"]: {"themes": r.get("themes", []), "problems": r.get("problems", [])} for r in results}
        n = write_tags(args.source, tags_by_url)
        print(f"Updated {n} rows in '{SCHEMAS[args.source]['worksheet']}'")


if __name__ == "__main__":
    _main_cli()
