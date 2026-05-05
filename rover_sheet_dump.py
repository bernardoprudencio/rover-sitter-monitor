"""
Rover Sitter Reddit → Google Sheets
────────────────────────────────────
Columns: Date | Title | URL | Author | Preview | Themes | Problems | Subreddit

Phase 1 (historical): HISTORICAL_MODE=true — fetches all available posts
Phase 2 (daily):      HISTORICAL_MODE=false — appends only new posts

Requirements:
    pip install gspread google-auth
"""

import urllib.request
import urllib.error
import xml.etree.ElementTree as ET
import re, os, time, json
from datetime import datetime, timezone

try:
    import gspread
    from google.oauth2.service_account import Credentials
except ImportError:
    print("Missing dependencies. Run: pip install gspread google-auth")
    exit(1)

# ── CONFIG ────────────────────────────────────────────────────────────────────
SUBREDDITS      = ["RoverPetSitting"]
SHEET_ID        = os.environ.get("SHEET_ID", "YOUR_GOOGLE_SHEET_ID_HERE")
CREDS_FILE      = os.environ.get("CREDS_FILE", "credentials.json")
HISTORICAL_MODE = os.environ.get("HISTORICAL_MODE", "false").lower() == "true"
MAX_POSTS       = 100
# ─────────────────────────────────────────────────────────────────────────────

# ── TAXONOMY (loaded from taxonomy.json — single source of truth) ────────────
_TAXONOMY_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "taxonomy.json")
try:
    with open(_TAXONOMY_PATH, "r", encoding="utf-8") as _f:
        _TAXONOMY = json.load(_f)
except FileNotFoundError:
    raise SystemExit(f"FATAL: taxonomy.json not found at {_TAXONOMY_PATH}")
except json.JSONDecodeError as _e:
    raise SystemExit(f"FATAL: taxonomy.json is invalid JSON: {_e}")

PROBLEMS         = {p: meta["keywords"] for p, meta in _TAXONOMY["problems"].items()}
PROBLEM_TO_THEME = {p: meta["theme"]    for p, meta in _TAXONOMY["problems"].items()}


def tag_post(title: str, text: str) -> tuple[list[str], list[str]]:
    """Return (matched_themes, matched_problems) for a post.

    Uses whole-word regex matching so short keywords like 'cat' don't
    fire inside unrelated words (e.g. 'appli**cat**ions').
    """
    combined = (title + " " + text).lower()
    matched_problems = []
    matched_themes   = []

    for problem, keywords in PROBLEMS.items():
        for kw in keywords:
            if re.search(r'\b' + re.escape(kw) + r'\b', combined):
                matched_problems.append(problem)
                theme = PROBLEM_TO_THEME.get(problem)
                if theme and theme not in matched_themes:
                    matched_themes.append(theme)
                break

    return (
        matched_themes   if matched_themes   else ["Untagged"],
        matched_problems if matched_problems else ["Untagged"],
    )


def strip_html(text: str) -> str:
    clean = re.sub(r"<[^>]+>", "", text)
    clean = re.sub(r"\[link\].*", "", clean)
    return clean.strip()


def fetch_posts(subreddit: str, after_ts: float = 0):
    """
    Fetch posts via pullpush.io — a free Reddit archive, no bot blocking.
    Falls back to Reddit RSS if pullpush fails.
    """
    import gzip
    results = _fetch_pullpush(subreddit, after_ts)
    if results is not None:
        return results
    print("  Falling back to Reddit RSS...")
    return _fetch_rss(subreddit, after_ts)


def _fetch_pullpush(subreddit: str, after_ts: float):
    """Try Arctic Shift first, then pullpush.io as backup."""
    result = _fetch_arctic_shift(subreddit, after_ts)
    if result is not None:
        return result

    # Fallback to pullpush.io
    params = f"subreddit={subreddit}&size={MAX_POSTS}&sort=desc&sort_type=created_utc"
    if after_ts > 0:
        params += f"&after={int(after_ts)}"
    url = f"https://api.pullpush.io/reddit/search/submission/?{params}"
    headers = {"User-Agent": "Mozilla/5.0 (compatible; rover-monitor/1.0)", "Accept": "application/json"}
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=20) as resp:
            raw = resp.read()
        data = json.loads(raw)
        entries = data.get("data", [])
        print(f"  pullpush.io: {len(entries)} posts")
        return _parse_pushshift_entries(entries)
    except Exception as ex:
        print(f"  pullpush.io failed: {ex}")
        return None


def _fetch_arctic_shift(subreddit: str, after_ts: float):
    """Fetch from Arctic Shift — reliable Reddit archive."""
    # Arctic Shift paginates with after= timestamp, fetch in batches
    after_param = int(after_ts)  # caller always provides a valid timestamp
    # Arctic Shift expects ISO date strings, not timestamps
    after_date = datetime.fromtimestamp(after_param, tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    url = f"https://arctic-shift.photon-reddit.com/api/posts/search?subreddit={subreddit}&after={after_date}&limit=100&sort_type=created_utc&sort=asc"
    print(f"  Arctic Shift URL: {url}")
    headers = {"User-Agent": "Mozilla/5.0 (compatible; rover-monitor/1.0)", "Accept": "application/json"}
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=20) as resp:
            raw = resp.read().decode("utf-8", errors="replace")
        data = json.loads(raw)
        entries = data.get("data", [])
        print(f"  Arctic Shift: {len(entries)} posts")
        if not entries:
            return None
        return _parse_pushshift_entries(entries)
    except Exception as ex:
        print(f"  Arctic Shift failed: {ex}")
        return None


def _parse_pushshift_entries(entries):
    now = time.time()
    posts = []
    for e in entries:
        created_utc = e.get("created_utc", 0)
        if isinstance(created_utc, str):
            try: created_utc = int(created_utc)
            except: created_utc = 0
        # Skip posts with future or invalid timestamps
        if created_utc <= 0 or created_utc > now:
            continue
        content = e.get("selftext", "").strip()
        if content in ("[removed]", "[deleted]"): content = ""
        title = e.get("title", "(no title)")
        themes, problems = tag_post(title, content)
        permalink = e.get("permalink", "")
        if not permalink.startswith("http"):
            permalink = f"https://reddit.com{permalink}"
        posts.append({
            "date":     datetime.fromtimestamp(created_utc, tz=timezone.utc).strftime("%Y-%m-%d %H:%M UTC"),
            "title":    title,
            "url":      permalink,
            "author":   e.get("author", "unknown"),
            "preview":  content[:500],
            "themes":   ", ".join(themes),
            "problems": ", ".join(problems),
            "ts":       created_utc,
        })
    posts.sort(key=lambda x: x["ts"])
    return posts


def _fetch_rss(subreddit: str, after_ts: float):
    import gzip
    url = f"https://www.reddit.com/r/{subreddit}/new/.rss?limit={MAX_POSTS}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
        "Accept": "application/rss+xml, application/xml, text/xml",
    }
    NS = {"atom": "http://www.w3.org/2005/Atom"}
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=15) as resp:
            raw_bytes = resp.read()
        try:
            raw = gzip.decompress(raw_bytes).decode("utf-8", errors="replace")
        except Exception:
            raw = raw_bytes.decode("utf-8", errors="replace")
        root = ET.fromstring(raw)
        entries = root.findall("atom:entry", NS)
        print(f"  RSS: {len(entries)} entries")
        posts = []
        for entry in entries:
            title   = entry.findtext("atom:title", default="", namespaces=NS)
            link_el = entry.find("atom:link", NS)
            url_val = link_el.get("href", "") if link_el is not None else ""
            author  = entry.findtext("atom:author/atom:name", default="unknown", namespaces=NS)
            updated = entry.findtext("atom:updated", default="", namespaces=NS)
            content = strip_html(entry.findtext("atom:content", default="", namespaces=NS))
            try:
                dt = datetime.fromisoformat(updated.replace("Z", "+00:00"))
                created_utc = dt.timestamp()
            except Exception:
                created_utc = time.time()
            if created_utc <= after_ts:
                continue
            themes, problems = tag_post(title, content)
            posts.append({
                "date":     datetime.fromtimestamp(created_utc, tz=timezone.utc).strftime("%Y-%m-%d %H:%M UTC"),
                "title":    title,
                "url":      url_val,
                "author":   author.replace("/u/", ""),
                "preview":  content[:500],
                "themes":   ", ".join(themes),
                "problems": ", ".join(problems),
                "ts":       created_utc,
            })
        posts.sort(key=lambda x: x["ts"])
        return posts
    except Exception as e:
        print(f"  RSS failed: {e}")
        return []


def get_sheet():
    scopes = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive",
    ]
    creds_json = os.environ.get("GOOGLE_CREDS_JSON")
    if creds_json:
        creds = Credentials.from_service_account_info(json.loads(creds_json), scopes=scopes)
    else:
        creds = Credentials.from_service_account_file(CREDS_FILE, scopes=scopes)

    client = gspread.authorize(creds)
    sheet  = client.open_by_key(SHEET_ID)

    try:
        ws = sheet.worksheet("Reddit Posts")
    except gspread.exceptions.WorksheetNotFound:
        ws = sheet.add_worksheet(title="Reddit Posts", rows=5000, cols=10)
        ws.append_row(["Date", "Title", "URL", "Author", "Preview", "Themes", "Problems", "Subreddit"])
        ws.format("A1:H1", {"textFormat": {"bold": True}})
    return ws


def get_latest_timestamp(ws) -> float:
    all_dates = ws.col_values(1)[1:]
    if not all_dates:
        return 0.0
    latest = max((d for d in all_dates if d), default="")
    if not latest:
        return 0.0
    try:
        dt = datetime.strptime(latest, "%Y-%m-%d %H:%M UTC").replace(tzinfo=timezone.utc)
        return dt.timestamp()
    except Exception:
        return 0.0


def retag_sheet(ws):
    """Re-run tag_post() on every existing row and update Themes/Problems columns in place."""
    print("Reading all rows from sheet...")
    all_rows = ws.get_all_values()
    if not all_rows or len(all_rows) < 2:
        print("  Sheet is empty or has only a header — nothing to retag.")
        return

    header   = all_rows[0]
    data_rows = all_rows[1:]
    print(f"  {len(data_rows)} posts to retag...")

    theme_updates   = []  # list of (row_index, new_value) — 1-based, skipping header
    problem_updates = []

    changed = 0
    for i, row in enumerate(data_rows):
        row_num = i + 2  # 1-based; +1 for header, +1 for 1-indexing
        title   = row[1] if len(row) > 1 else ""
        preview = row[4] if len(row) > 4 else ""
        old_themes   = row[5] if len(row) > 5 else ""
        old_problems = row[6] if len(row) > 6 else ""

        new_themes, new_problems = tag_post(title, preview)
        new_themes_str   = ", ".join(new_themes)
        new_problems_str = ", ".join(new_problems)

        theme_updates.append([new_themes_str])
        problem_updates.append([new_problems_str])

        if new_themes_str != old_themes or new_problems_str != old_problems:
            changed += 1

    # Batch-update columns F and G (themes=6, problems=7) in one API call each
    start_row = 2  # skip header
    end_row   = 1 + len(data_rows)

    ws.update(f"F{start_row}:F{end_row}", theme_updates,   value_input_option="RAW")
    ws.update(f"G{start_row}:G{end_row}", problem_updates, value_input_option="RAW")

    print(f"  ✅ Retagged {len(data_rows)} rows — {changed} tags changed.")


def append_posts(ws, posts: list[dict], subreddit: str):
    if not posts:
        print("  No new posts to append.")
        return
    rows = [
        [p["date"], p["title"], p["url"], p["author"],
         p["preview"], p["themes"], p["problems"], subreddit]
        for p in posts
    ]
    ws.append_rows(rows, value_input_option="RAW")
    print(f"  ✅ Appended {len(rows)} posts to sheet.")


def main():
    import sys
    retag_mode = "--retag" in sys.argv

    print("Connecting to Google Sheets...")
    ws = get_sheet()

    if retag_mode:
        print("🔁 RETAG MODE — re-tagging all existing rows with improved matching")
        retag_sheet(ws)
        print("\nDone!")
        return

    if HISTORICAL_MODE:
        print("📚 HISTORICAL MODE — paginating from Jan 1 2025 to today")
        for sub in SUBREDDITS:
            print(f"\nFetching r/{sub}...")
            cursor    = 1735689600  # Jan 1 2025 00:00 UTC
            end_ts    = time.time()
            batch_num = 0
            total     = 0
            while cursor < end_ts:
                batch_num += 1
                batch_date = datetime.fromtimestamp(cursor, tz=timezone.utc).strftime("%Y-%m-%d")
                print(f"  Batch {batch_num} — from {batch_date}")
                batch = _fetch_arctic_shift(sub, cursor)
                if not batch:
                    print("  No more posts found, stopping.")
                    break
                append_posts(ws, batch, sub)
                total  += len(batch)
                cursor  = batch[-1]["ts"] + 1
                print(f"  → {len(batch)} posts appended (total: {total})")
                time.sleep(1)
                if len(batch) < 2:
                    print("  Reached end of available data.")
                    break
            print(f"  Done — {total} posts written across {batch_num} batches")
    else:
        after_ts = get_latest_timestamp(ws)
        if after_ts:
            print(f"📅 DAILY MODE — fetching posts newer than {datetime.fromtimestamp(after_ts, tz=timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}")
        else:
            print("📅 DAILY MODE — sheet is empty, fetching all available posts")
        for sub in SUBREDDITS:
            print(f"\nFetching r/{sub}...")
            posts = fetch_posts(sub, after_ts=after_ts)
            print(f"  {len(posts)} new posts found")
            append_posts(ws, posts, sub)

    print("\nDone!")


if __name__ == "__main__":
    main()
