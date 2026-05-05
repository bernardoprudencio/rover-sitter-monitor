"""
Rover Confluence Research → Google Sheets
─────────────────────────────────────────
Columns: PageID | Updated | Space | Title | URL | Author | Excerpt | Themes | Problems | Labels

Fetches pages from internal Confluence spaces (default: DSN, PSD), tags them
against taxonomy.json using rover_sheet_dump.tag_post (same matcher as Reddit),
and upserts into a "Confluence Research" tab on the same Google Sheet.

Modes:
    default        — incremental: pull pages modified since the cursor stored
                     in the `confluence_meta` worksheet, upsert by PageID.
    --retag        — re-run tag_post on existing rows in place (no fetch).
                     Use after taxonomy.json edits, mirroring rover_sheet_dump.py.
    --full         — ignore cursor and re-fetch every page (first run / recovery).
    --limit N      — cap pages fetched per space (smoke testing).
    --space KEY    — restrict to a single space (overrides CONFLUENCE_SPACE_KEYS).

Requirements:
    pip install gspread google-auth requests beautifulsoup4
"""

from __future__ import annotations

import argparse
import os
import re
import sys
import time
from datetime import datetime, timezone
from typing import Iterator

try:
    import gspread
    import requests
    from bs4 import BeautifulSoup
    from google.oauth2.service_account import Credentials
    from requests.auth import HTTPBasicAuth
except ImportError as e:
    print(f"Missing dependency: {e}. Run: pip install gspread google-auth requests beautifulsoup4")
    sys.exit(1)

from rover_sheet_dump import tag_post

# ── CONFIG ────────────────────────────────────────────────────────────────────
SHEET_ID            = os.environ.get("SHEET_ID", "YOUR_GOOGLE_SHEET_ID_HERE")
CREDS_FILE          = os.environ.get("CREDS_FILE", "credentials.json")
CONFLUENCE_DOMAIN   = os.environ.get("CONFLUENCE_DOMAIN", "roverdotcom.atlassian.net")
CONFLUENCE_EMAIL    = os.environ.get("CONFLUENCE_EMAIL", "")
CONFLUENCE_TOKEN    = os.environ.get("CONFLUENCE_API_TOKEN", "")
DEFAULT_SPACE_KEYS  = os.environ.get("CONFLUENCE_SPACE_KEYS", "DSN,PSD")

WORKSHEET_NAME      = "Confluence Research"
META_WORKSHEET_NAME = "confluence_meta"
EXCERPT_MAX         = 500  # match rover_export_json.PREVIEW_MAX
PAGE_FETCH_LIMIT    = 100  # per Confluence v2 API call
COLUMNS             = ["PageID", "Updated", "Space", "Title", "URL",
                       "Author", "Excerpt", "Themes", "Problems", "Labels"]
# ─────────────────────────────────────────────────────────────────────────────


# ── Confluence API ────────────────────────────────────────────────────────────

def _api_base() -> str:
    return f"https://{CONFLUENCE_DOMAIN}/wiki/api/v2"


def _auth() -> HTTPBasicAuth:
    if not CONFLUENCE_EMAIL or not CONFLUENCE_TOKEN:
        raise SystemExit(
            "FATAL: CONFLUENCE_EMAIL and CONFLUENCE_API_TOKEN must be set "
            "(create a token at https://id.atlassian.com/manage-profile/security/api-tokens)"
        )
    return HTTPBasicAuth(CONFLUENCE_EMAIL, CONFLUENCE_TOKEN)


def _get(path: str, params: dict | None = None) -> dict:
    url = path if path.startswith("http") else f"{_api_base()}{path}"
    r = requests.get(url, params=params, auth=_auth(), timeout=30,
                     headers={"Accept": "application/json"})
    r.raise_for_status()
    return r.json()


def resolve_space_ids(space_keys: list[str]) -> list[tuple[str, str]]:
    """Return [(key, id), ...] for the given space keys. Skips keys that don't resolve."""
    result: list[tuple[str, str]] = []
    # v2 supports keys=DSN,PSD as a comma-separated query
    data = _get("/spaces", params={"keys": ",".join(space_keys), "limit": 250})
    by_key = {s["key"]: s["id"] for s in data.get("results", [])}
    for k in space_keys:
        if k in by_key:
            result.append((k, by_key[k]))
        else:
            print(f"  ⚠ space key {k!r} not found / not accessible — skipping")
    return result


def iter_pages(space_id: str, since_iso: str | None) -> Iterator[dict]:
    """Yield raw page dicts from Confluence v2 API, paginated.

    Confluence v2 doesn't accept a server-side `since` filter on
    /spaces/{id}/pages, so we filter client-side by version.createdAt.
    """
    cursor: str | None = None
    while True:
        params = {
            "limit": PAGE_FETCH_LIMIT,
            "body-format": "storage",
            "sort": "-modified-date",
        }
        if cursor:
            params["cursor"] = cursor
        data = _get(f"/spaces/{space_id}/pages", params=params)
        results = data.get("results", [])
        if not results:
            return
        cutoff_reached = False
        for page in results:
            updated = page.get("version", {}).get("createdAt", "")
            if since_iso and updated and updated <= since_iso:
                cutoff_reached = True
                break
            yield page
        if cutoff_reached:
            return
        next_link = data.get("_links", {}).get("next")
        if not next_link:
            return
        # next_link is relative like "/wiki/api/v2/spaces/.../pages?cursor=..."
        m = re.search(r"cursor=([^&]+)", next_link)
        if not m:
            return
        cursor = requests.utils.unquote(m.group(1))


def page_url(page: dict) -> str:
    webui = page.get("_links", {}).get("webui", "")
    if webui.startswith("http"):
        return webui
    return f"https://{CONFLUENCE_DOMAIN}/wiki{webui}"


def page_author(page: dict) -> str:
    """Resolve author display name from accountId via /users/{id}.

    Cached per run to avoid N round-trips for the same author.
    """
    acct = page.get("authorId") or page.get("ownerId") or ""
    if not acct:
        return "unknown"
    cached = _AUTHOR_CACHE.get(acct)
    if cached is not None:
        return cached
    try:
        # v1 endpoint — v2 doesn't expose user lookup
        url = f"https://{CONFLUENCE_DOMAIN}/wiki/rest/api/user?accountId={acct}"
        r = requests.get(url, auth=_auth(), timeout=15)
        if r.status_code == 200:
            name = r.json().get("displayName", acct)
        else:
            name = acct
    except Exception:
        name = acct
    _AUTHOR_CACHE[acct] = name
    return name


_AUTHOR_CACHE: dict[str, str] = {}


def page_labels(page_id: str) -> list[str]:
    """Fetch labels for a page (separate API call). Returns empty list on failure."""
    try:
        data = _get(f"/pages/{page_id}/labels", params={"limit": 100})
        return [lbl.get("name", "") for lbl in data.get("results", []) if lbl.get("name")]
    except Exception:
        return []


def extract_plain(storage_html: str) -> str:
    """Strip Confluence storage-format XHTML to plain text, collapse whitespace."""
    if not storage_html:
        return ""
    soup = BeautifulSoup(storage_html, "html.parser")
    text = soup.get_text(" ")
    return re.sub(r"\s+", " ", text).strip()


def truncate(s: str, n: int = EXCERPT_MAX) -> str:
    if len(s) <= n:
        return s
    cut = s[:n]
    sp = cut.rfind(" ")
    return (cut[:sp] if sp > 0 else cut).rstrip() + "…"


# ── Google Sheets ─────────────────────────────────────────────────────────────

def get_sheet():
    """Open the spreadsheet (same auth pattern as rover_sheet_dump.get_sheet)."""
    import json as _json
    scopes = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive",
    ]
    creds_json = os.environ.get("GOOGLE_CREDS_JSON")
    if creds_json:
        creds = Credentials.from_service_account_info(_json.loads(creds_json), scopes=scopes)
    else:
        creds = Credentials.from_service_account_file(CREDS_FILE, scopes=scopes)
    return gspread.authorize(creds).open_by_key(SHEET_ID)


def get_research_ws(sheet):
    try:
        ws = sheet.worksheet(WORKSHEET_NAME)
    except gspread.exceptions.WorksheetNotFound:
        ws = sheet.add_worksheet(title=WORKSHEET_NAME, rows=2000, cols=len(COLUMNS))
        ws.append_row(COLUMNS)
        ws.format(f"A1:{chr(ord('A') + len(COLUMNS) - 1)}1", {"textFormat": {"bold": True}})
    return ws


def get_meta_ws(sheet):
    try:
        return sheet.worksheet(META_WORKSHEET_NAME)
    except gspread.exceptions.WorksheetNotFound:
        ws = sheet.add_worksheet(title=META_WORKSHEET_NAME, rows=10, cols=2)
        ws.append_row(["key", "value"])
        return ws


def read_cursor(meta_ws) -> str | None:
    rows = meta_ws.get_all_values()
    for r in rows[1:]:
        if r and r[0] == "last_run_utc" and len(r) > 1 and r[1]:
            return r[1]
    return None


def write_cursor(meta_ws, iso_value: str) -> None:
    rows = meta_ws.get_all_values()
    for i, r in enumerate(rows):
        if r and r[0] == "last_run_utc":
            meta_ws.update(f"B{i + 1}", [[iso_value]], value_input_option="RAW")
            return
    meta_ws.append_row(["last_run_utc", iso_value], value_input_option="RAW")


def upsert_rows(ws, records: list[list[str]]) -> tuple[int, int]:
    """Upsert by PageID (column A). Returns (new_count, updated_count)."""
    if not records:
        return 0, 0
    existing = ws.get_all_values()
    header = existing[0] if existing else COLUMNS
    id_to_row = {row[0]: i + 2 for i, row in enumerate(existing[1:]) if row and row[0]}

    appends: list[list[str]] = []
    updates: list[tuple[int, list[str]]] = []
    for rec in records:
        pid = rec[0]
        if pid in id_to_row:
            updates.append((id_to_row[pid], rec))
        else:
            appends.append(rec)

    if appends:
        ws.append_rows(appends, value_input_option="RAW")
    for row_num, rec in updates:
        ws.update(f"A{row_num}:{chr(ord('A') + len(COLUMNS) - 1)}{row_num}",
                  [rec], value_input_option="RAW")

    return len(appends), len(updates)


# ── Modes ─────────────────────────────────────────────────────────────────────

def build_record(page: dict, space_key: str) -> list[str]:
    pid       = str(page.get("id", ""))
    title     = page.get("title", "(untitled)")
    updated   = page.get("version", {}).get("createdAt", "")
    body_html = (page.get("body", {}) or {}).get("storage", {}).get("value", "")
    plain     = extract_plain(body_html)
    excerpt   = truncate(plain)
    themes, problems = tag_post(title, plain)
    labels    = page_labels(pid)
    author    = page_author(page)
    return [
        pid,
        updated,
        space_key,
        title,
        page_url(page),
        author,
        excerpt,
        ", ".join(themes),
        ", ".join(problems),
        ", ".join(labels),
    ]


def run_dump(args):
    space_keys = [args.space] if args.space else [k.strip() for k in DEFAULT_SPACE_KEYS.split(",") if k.strip()]
    print(f"Spaces: {space_keys}")

    print("Connecting to Google Sheets...")
    sheet = get_sheet()
    ws = get_research_ws(sheet)
    meta_ws = get_meta_ws(sheet)

    cursor = None if args.full else read_cursor(meta_ws)
    if cursor:
        print(f"Cursor: incremental since {cursor}")
    else:
        print("Cursor: none — full ingest")

    spaces = resolve_space_ids(space_keys)
    if not spaces:
        print("No accessible spaces. Aborting.")
        return

    started_at = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    total_records: list[list[str]] = []

    for space_key, space_id in spaces:
        print(f"\nFetching pages from {space_key} (id={space_id})...")
        count = 0
        for page in iter_pages(space_id, since_iso=cursor):
            total_records.append(build_record(page, space_key))
            count += 1
            if args.limit and count >= args.limit:
                print(f"  hit --limit {args.limit}")
                break
        print(f"  {count} pages fetched")

    if not total_records:
        print("\nNo new pages to write.")
    else:
        print(f"\nUpserting {len(total_records)} records into '{WORKSHEET_NAME}'...")
        new, upd = upsert_rows(ws, total_records)
        print(f"  ✅ {new} new, {upd} updated")

    # Skip cursor advance on --limit runs — they're smoke tests, not full
    # ingests. Otherwise the next scheduled run would think there is nothing
    # to do and the rest of the corpus would never get fetched.
    if args.limit:
        print(f"⏸  --limit {args.limit} run — cursor NOT advanced (re-run without --limit to fully ingest)")
    else:
        write_cursor(meta_ws, started_at)
        print(f"Cursor advanced to {started_at}")


def run_retag(_args):
    print("🔁 RETAG MODE — re-tagging Confluence rows in place")
    print("Connecting to Google Sheets...")
    sheet = get_sheet()
    ws = get_research_ws(sheet)

    rows = ws.get_all_values()
    if len(rows) < 2:
        print("  Sheet has no data rows — nothing to retag.")
        return

    header   = rows[0]
    data     = rows[1:]
    print(f"  {len(data)} rows to retag...")

    theme_updates: list[list[str]] = []
    problem_updates: list[list[str]] = []
    changed = 0

    for r in data:
        title   = r[3] if len(r) > 3 else ""
        excerpt = r[6] if len(r) > 6 else ""
        old_t   = r[7] if len(r) > 7 else ""
        old_p   = r[8] if len(r) > 8 else ""
        themes, problems = tag_post(title, excerpt)
        new_t = ", ".join(themes)
        new_p = ", ".join(problems)
        theme_updates.append([new_t])
        problem_updates.append([new_p])
        if new_t != old_t or new_p != old_p:
            changed += 1

    end_row = 1 + len(data)
    # Themes column is H (index 7 → "H"), Problems is I (index 8 → "I")
    ws.update(f"H2:H{end_row}", theme_updates, value_input_option="RAW")
    ws.update(f"I2:I{end_row}", problem_updates, value_input_option="RAW")
    print(f"  ✅ Retagged {len(data)} rows — {changed} tags changed.")


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--retag", action="store_true",
                    help="Re-tag existing rows in place; no Confluence fetch.")
    ap.add_argument("--full", action="store_true",
                    help="Ignore the stored cursor and re-fetch every page.")
    ap.add_argument("--limit", type=int, default=0,
                    help="Cap pages per space (smoke testing).")
    ap.add_argument("--space", type=str, default="",
                    help="Single space key (overrides CONFLUENCE_SPACE_KEYS).")
    args = ap.parse_args()

    if args.retag:
        run_retag(args)
    else:
        run_dump(args)
    print("\nDone!")


if __name__ == "__main__":
    main()
