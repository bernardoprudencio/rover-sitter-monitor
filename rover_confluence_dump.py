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
    --inspect      — read-only: snapshot the existing sheet (label / title /
                     author distributions + a 75-row random sample at seed
                     20260505) into reviews/<date>-confluence-discovery.{md,json}.
                     Used to design the eligibility filter from real data.
    --no-filter    — bypass evaluate_eligibility (every row marked
                     Eligible="yes", FilterReason="bypassed"). Debug only.

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
                       "Author", "Excerpt", "Themes", "Problems", "Labels",
                       "Eligible", "FilterReason"]
# ─────────────────────────────────────────────────────────────────────────────


# ── ELIGIBILITY FILTER ────────────────────────────────────────────────────────
# Two gates, both must pass:
#   1. Doc-type — is this a finished research finding (vs. plan / script /
#      meeting note / retro / draft)?
#   2. Audience — provider-relevant (sitter / walker / trainer / groomer /
#      provider / host)? PSD admits by default; DSN must show provider terms
#      in title or body.
#
# Rule derivation lives in reviews/<date>-confluence-filter-rules-derivation.md
# (75-row sample at seed 20260505 from reviews/<date>-confluence-discovery.md).
# Audit accuracy is tracked round-by-round in reviews/<date>-confluence-filter-roundN.md.

NON_FINDINGS_LABELS = frozenset({
    "meeting-notes", "okrs", "projectplan", "project",
    "org-chart", "file-list", "figma", "kb-how-to-article",
    "shared-links", "marketing-campaigns",
})

# Title patterns that disqualify a page regardless of other signals.
NON_FINDINGS_TITLE_RE = re.compile(
    # Date-prefix meeting notes: "2018-06-19 Design Sync", "2024-09-16 Design Check-in"
    r"^\d{4}[-/]\d{1,2}[-/]\d{1,2}\b"
    # Preparation / planning / org / draft prefixes
    r"|^(script|screener|recruiting|research\s+plan|study\s+plan|discussion\s+guide|"
    r"conjoint\s+design|design\s+exploration|vision|proposal|draft|wip|temp|template|"
    r"agenda|kick[\s-]?off|retro|rfc|spec|standup|sync|meeting\s+notes|session\s+notes|"
    r"test\s+session\s+notes|interview\s+notes|interview\s+transcript|notes\s+from|"
    r"okrs?|q[1-4]\s+\d{4}|january\s+ideation|red\s+routes|rover\s+history|"
    r"product\s+partners|resources?[\s\-:]|fonts?$|figma\b|matteo\s+q[1-4]|gino\s+okr|"
    r"upwork|email\s+#|checklist)\b"
    # Recurring meeting / planning markers anywhere in the title
    r"|\b(meeting\s+notes|design\s+check[\s-]?in|design\s+sync|"
    r"growth\s+(design\s+|project\s+)?sync|working\s+session|stand[\s-]?up|"
    r"all[\s-]?hands|kick[\s-]?off|okr\s+timelines?|hiring\s+interview|"
    r"checklist|survey\s+request)\b"
    # WIP / draft / template markers anywhere
    r"|\(wip\)|\bwip\b|[\(\[]draft[\)\]]|\[temp\b|\btemplate\b|\bplaceholder\b",
    re.IGNORECASE,
)

# Title patterns that mark a page as a finding/research output.
FINDINGS_TITLE_RE = re.compile(
    r"^(findings(\s+report)?|early\s+findings|round\s+\d+\s+findings|key\s+findings|"
    r"insights?(\s+assessment)?|key\s+insights?|read[\s-]?out|report|reports|results|"
    r"write[\s-]?up|desk\s+research|survey\s+results|study\s+results|"
    r"acceleration\s+#?\d+)\b"
    r"|:\s*(findings|write[\s-]?up|insights?|results|report)\s*$",
    re.IGNORECASE,
)

# Provider-research escape hatch: a `<provider> survey` is a finding even
# without an explicit findings prefix (e.g. "Sitter Non-response Survey - 2022").
PROVIDER_SURVEY_RE = re.compile(
    r"\b(sitter|walker|trainer|groomer|provider|host)s?\b.{0,40}\bsurvey\b",
    re.IGNORECASE,
)

PROVIDER_TERMS_RE = re.compile(
    r"\b(sitter|sitters|walker|walkers|trainer|trainers|groomer|groomers|"
    r"provider|providers|host|hosts|hosting|sitting|boarding|daycare|"
    r"drop[\s-]?in|drop[\s-]?off|m&g|meet\s+and\s+greet|caregiver|"
    r"pet\s+care\s+professional|pet\s+pro|pet\s+sitter|dog\s+walker|"
    r"dog\s+walking|cat\s+sitter|service\s+provider)\b",
    re.IGNORECASE,
)


def evaluate_eligibility(
    title: str, body: str, labels: list[str], space: str
) -> tuple[bool, str]:
    """Decide if a Confluence page belongs in the dashboard.

    Returns (eligible, reason_code). Empty reason iff eligible.
    Pure function — no I/O. See module docstring for the derivation.
    """
    title = (title or "").strip()
    title_l = title.lower()

    # 1. Label blocklist — trumps title signals.
    for lbl in (labels or []):
        if lbl.lower() in NON_FINDINGS_LABELS:
            return False, f"non_findings_label:{lbl.lower()}"

    # 2. Title blocklist.
    block_match = NON_FINDINGS_TITLE_RE.search(title_l)
    if block_match:
        snippet = block_match.group(0)[:30]
        return False, f"non_findings_title:{snippet}"

    # 3. Title whitelist (or provider-survey escape hatch).
    if not (FINDINGS_TITLE_RE.search(title_l) or PROVIDER_SURVEY_RE.search(title_l)):
        return False, "no_findings_signal"

    # 4. Audience.
    if space == "PSD":
        return True, ""
    haystack = f"{title}\n{body or ''}"
    if PROVIDER_TERMS_RE.search(haystack):
        return True, ""
    return False, "non_provider:dsn_no_provider_terms"

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
            meta_ws.update(values=[[iso_value]], range_name=f"B{i + 1}", value_input_option="RAW")
            return
    meta_ws.append_row(["last_run_utc", iso_value], value_input_option="RAW")


def upsert_rows(ws, records: list[list[str]]) -> tuple[int, int]:
    """Upsert by PageID (column A). Returns (new_count, updated_count).

    Updates are sent via a single batch_update call to stay under the Sheets
    per-user/per-minute write quota (default 60). Earlier per-row update()
    loops blew the quota on the first full DSN ingest (1.4k pages).
    """
    if not records:
        return 0, 0
    existing = ws.get_all_values()
    id_to_row = {row[0]: i + 2 for i, row in enumerate(existing[1:]) if row and row[0]}

    end_col = chr(ord("A") + len(COLUMNS) - 1)
    appends: list[list[str]] = []
    updates: list[dict] = []
    for rec in records:
        pid = rec[0]
        if pid in id_to_row:
            row_num = id_to_row[pid]
            updates.append({"range": f"A{row_num}:{end_col}{row_num}", "values": [rec]})
        else:
            appends.append(rec)

    if appends:
        ws.append_rows(appends, value_input_option="RAW")
    if updates:
        ws.batch_update(updates, value_input_option="RAW")

    return len(appends), len(updates)


# ── Modes ─────────────────────────────────────────────────────────────────────

def build_record(page: dict, space_key: str, bypass_filter: bool = False) -> list[str]:
    pid       = str(page.get("id", ""))
    title     = page.get("title", "(untitled)")
    updated   = page.get("version", {}).get("createdAt", "")
    body_html = (page.get("body", {}) or {}).get("storage", {}).get("value", "")
    plain     = extract_plain(body_html)
    excerpt   = truncate(plain)
    themes, problems = tag_post(title, plain)
    labels    = page_labels(pid)
    author    = page_author(page)
    if bypass_filter:
        eligible, reason = True, "bypassed"
    else:
        eligible, reason = evaluate_eligibility(title, plain, labels, space_key)
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
        "yes" if eligible else "no",
        reason,
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
            total_records.append(build_record(page, space_key, bypass_filter=args.no_filter))
            count += 1
            if args.limit and count >= args.limit:
                print(f"  hit --limit {args.limit}")
                break
        print(f"  {count} pages fetched")
    if not args.no_filter:
        eligible_n = sum(1 for r in total_records if len(r) > 10 and r[10] == "yes")
        print(f"\nFilter: {eligible_n}/{len(total_records)} eligible "
              f"({(100*eligible_n/len(total_records)) if total_records else 0:.1f}%)")

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


def run_inspect(_args):
    """Read-only inspection of the Confluence Research sheet.

    No Confluence API calls, no writes to the sheet. Produces a markdown
    report and a JSON sidecar in reviews/ that capture the data needed to
    design the eligibility filter (label frequency, title prefix patterns,
    author distribution, and a fixed random sample for manual classification).
    """
    import json as _json
    import random
    from collections import Counter
    from datetime import date

    print("🔍 INSPECT MODE — read-only sheet snapshot")
    print("Connecting to Google Sheets...")
    sheet = get_sheet()
    ws = get_research_ws(sheet)

    rows = ws.get_all_values()
    if len(rows) < 2:
        print("  Sheet has no data rows — nothing to inspect.")
        return

    header = rows[0]
    data = rows[1:]
    print(f"  {len(data)} rows in '{WORKSHEET_NAME}'")

    idx = {name: i for i, name in enumerate(header)}

    def col(row: list[str], name: str, default: str = "") -> str:
        i = idx.get(name)
        if i is None or i >= len(row):
            return default
        return row[i] or default

    space_counts: Counter = Counter(col(r, "Space") for r in data)

    label_counts: Counter = Counter()
    label_to_titles: dict[str, list[str]] = {}
    no_label_count = 0
    for r in data:
        labels = [l.strip() for l in col(r, "Labels").split(",") if l.strip()]
        if not labels:
            no_label_count += 1
        title = col(r, "Title")
        for lbl in labels:
            label_counts[lbl] += 1
            samples = label_to_titles.setdefault(lbl, [])
            if len(samples) < 3 and title and title not in samples:
                samples.append(title)

    first_word_counts: Counter = Counter()
    prefix_counts: Counter = Counter()
    for r in data:
        title = col(r, "Title").strip()
        if not title:
            continue
        m = re.match(r"^[\(\[]?\s*([^\s:|—–\-]+)", title)
        if m:
            first_word_counts[m.group(1).lower().rstrip(",.:;")] += 1
        m2 = re.match(r"^([^:—–|]{2,60})[:—–|]\s+\S", title)
        if m2:
            prefix_counts[m2.group(1).strip().lower()] += 1

    author_counts: Counter = Counter(col(r, "Author") for r in data)

    rng = random.Random(20260505)
    sample_size = min(75, len(data))
    sampled = rng.sample(data, sample_size)
    sample_records = [
        {
            "id": col(r, "PageID"),
            "space": col(r, "Space"),
            "title": col(r, "Title"),
            "author": col(r, "Author"),
            "labels": [l.strip() for l in col(r, "Labels").split(",") if l.strip()],
            "themes": [t.strip() for t in col(r, "Themes").split(",") if t.strip()],
            "problems": [p.strip() for p in col(r, "Problems").split(",") if p.strip()],
            "excerpt": col(r, "Excerpt"),
            "url": col(r, "URL"),
        }
        for r in sampled
    ]

    today = date.today().isoformat()
    reviews_dir = "reviews"
    os.makedirs(reviews_dir, exist_ok=True)
    json_path = os.path.join(reviews_dir, f"{today}-confluence-discovery.json")
    md_path = os.path.join(reviews_dir, f"{today}-confluence-discovery.md")

    sidecar = {
        "generated_at_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "total_rows": len(data),
        "header": header,
        "space_counts": dict(space_counts),
        "no_label_count": no_label_count,
        "top_labels": [
            {"label": lbl, "count": n, "sample_titles": label_to_titles.get(lbl, [])}
            for lbl, n in label_counts.most_common(50)
        ],
        "top_first_words": [{"word": w, "count": n} for w, n in first_word_counts.most_common(30)],
        "top_prefixes": [{"prefix": p, "count": n} for p, n in prefix_counts.most_common(30)],
        "top_authors": [{"author": a, "count": n} for a, n in author_counts.most_common(20)],
        "sample_seed": 20260505,
        "sample_size": sample_size,
        "sample": sample_records,
    }
    with open(json_path, "w", encoding="utf-8") as f:
        _json.dump(sidecar, f, ensure_ascii=False, indent=2)

    def md_safe(s: str) -> str:
        return (s or "").replace("|", "\\|").replace("\n", " ")

    lines: list[str] = []
    lines.append(f"# Confluence Research — Sheet Inspection ({today})")
    lines.append("")
    lines.append("Read-only snapshot of the `Confluence Research` tab to inform filter design.")
    lines.append(f"Sidecar: [{os.path.basename(json_path)}]({os.path.basename(json_path)})")
    lines.append("")
    lines.append("## Summary")
    lines.append("")
    lines.append(f"- **Total rows:** {len(data)}")
    pct_no_label = (100.0 * no_label_count / len(data)) if data else 0.0
    lines.append(f"- **Rows with no label:** {no_label_count} ({pct_no_label:.1f}%)")
    lines.append("")
    lines.append("### Space distribution")
    lines.append("")
    lines.append("| Space | Count |")
    lines.append("|---|---|")
    for sp, n in space_counts.most_common():
        lines.append(f"| {md_safe(sp) or '(blank)'} | {n} |")
    lines.append("")
    lines.append("## Top 50 labels")
    lines.append("")
    lines.append("| Label | Count | Sample titles |")
    lines.append("|---|---|---|")
    for lbl, n in label_counts.most_common(50):
        samples = " · ".join(t[:60] for t in label_to_titles.get(lbl, []))
        lines.append(f"| `{md_safe(lbl)}` | {n} | {md_safe(samples)} |")
    lines.append("")
    lines.append("## Top 30 title first-words")
    lines.append("")
    lines.append("| First word | Count |")
    lines.append("|---|---|")
    for w, n in first_word_counts.most_common(30):
        lines.append(f"| `{md_safe(w)}` | {n} |")
    lines.append("")
    lines.append("## Top 30 title prefixes (text before `:` / `—` / `|`)")
    lines.append("")
    lines.append("| Prefix | Count |")
    lines.append("|---|---|")
    for p, n in prefix_counts.most_common(30):
        lines.append(f"| `{md_safe(p)}` | {n} |")
    lines.append("")
    lines.append("## Top 20 authors")
    lines.append("")
    lines.append("| Author | Count |")
    lines.append("|---|---|")
    for a, n in author_counts.most_common(20):
        lines.append(f"| {md_safe(a) or '(blank)'} | {n} |")
    lines.append("")
    lines.append(f"## Random sample of {sample_size} rows (seed `20260505`)")
    lines.append("")
    lines.append("Full data in the JSON sidecar. Manifest below — use the sidecar for classification.")
    lines.append("")
    lines.append("| # | Space | Title | Author | Labels |")
    lines.append("|---|---|---|---|---|")
    for i, rec in enumerate(sample_records, 1):
        title = md_safe((rec["title"] or "")[:80])
        labels = md_safe(", ".join(rec["labels"])[:40])
        author = md_safe(rec["author"])
        lines.append(f"| {i} | {rec['space']} | {title} | {author} | {labels} |")
    lines.append("")

    with open(md_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    print(f"  ✅ Wrote {md_path}")
    print(f"  ✅ Wrote {json_path}")


def run_retag(args):
    print("🔁 RETAG MODE — re-tagging + re-evaluating eligibility on Confluence rows")
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

    # Ensure the sheet has 12 columns + headers — pre-filter sheets have 10.
    old_col_count = ws.col_count
    if old_col_count < len(COLUMNS):
        ws.add_cols(len(COLUMNS) - old_col_count)
        print(f"  ↪ Extended sheet from {old_col_count} to {len(COLUMNS)} columns")
    if len(header) < len(COLUMNS):
        new_header = list(COLUMNS)
        ws.update(values=[new_header], range_name="A1:L1", value_input_option="RAW")
        ws.format("K1:L1", {"textFormat": {"bold": True}})
        print(f"  ↪ Extended header from {len(header)} to {len(new_header)} columns")

    bypass = getattr(args, "no_filter", False)
    updates: list[list[str]] = []  # H..L for each row
    tag_changed = 0
    elig_changed = 0
    elig_yes = 0

    for r in data:
        title   = r[3] if len(r) > 3 else ""
        excerpt = r[6] if len(r) > 6 else ""
        space   = r[2] if len(r) > 2 else ""
        labels  = [l.strip() for l in (r[9] if len(r) > 9 else "").split(",") if l.strip()]
        old_t   = r[7] if len(r) > 7 else ""
        old_p   = r[8] if len(r) > 8 else ""
        old_e   = r[10] if len(r) > 10 else ""
        old_r   = r[11] if len(r) > 11 else ""

        themes, problems = tag_post(title, excerpt)
        new_t = ", ".join(themes)
        new_p = ", ".join(problems)

        if bypass:
            eligible, reason = True, "bypassed"
        else:
            # Use excerpt as proxy for body (full body isn't stored). 500 chars
            # of plain text is usually enough to spot provider terms; if not,
            # body-less FNs will surface in the audit and we can re-fetch.
            eligible, reason = evaluate_eligibility(title, excerpt, labels, space)
        new_e = "yes" if eligible else "no"

        updates.append([new_t, new_p, "", "", new_e, reason])
        if new_t != old_t or new_p != old_p:
            tag_changed += 1
        if new_e != old_e or reason != old_r:
            elig_changed += 1
        if eligible:
            elig_yes += 1

    end_row = 1 + len(data)
    # H = Themes, I = Problems, K = Eligible, L = FilterReason. We avoid a
    # single H..L batch because that range covers J (Labels) and writing ""
    # there would clobber existing label data. Four targeted column writes
    # are the simplest way to leave J alone.
    theme_col    = [[u[0]] for u in updates]
    problem_col  = [[u[1]] for u in updates]
    eligible_col = [[u[4]] for u in updates]
    reason_col   = [[u[5]] for u in updates]
    ws.update(values=theme_col,    range_name=f"H2:H{end_row}", value_input_option="RAW")
    ws.update(values=problem_col,  range_name=f"I2:I{end_row}", value_input_option="RAW")
    ws.update(values=eligible_col, range_name=f"K2:K{end_row}", value_input_option="RAW")
    ws.update(values=reason_col,   range_name=f"L2:L{end_row}", value_input_option="RAW")

    pct = (100.0 * elig_yes / len(data)) if data else 0.0
    print(f"  ✅ Retagged {len(data)} rows — {tag_changed} tag changes, "
          f"{elig_changed} eligibility changes.")
    print(f"  Eligible: {elig_yes}/{len(data)} ({pct:.1f}%)")


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
    ap.add_argument("--inspect", action="store_true",
                    help="Read-only snapshot of the sheet for filter design; "
                         "writes reviews/<date>-confluence-discovery.{md,json}.")
    ap.add_argument("--no-filter", action="store_true",
                    help="Bypass the eligibility filter (Eligible='yes', "
                         "FilterReason='bypassed'). For debugging / audit dumps.")
    args = ap.parse_args()

    if args.inspect:
        run_inspect(args)
    elif args.retag:
        run_retag(args)
    else:
        run_dump(args)
    print("\nDone!")


if __name__ == "__main__":
    main()
