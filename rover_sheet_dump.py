"""
Rover Sitter Reddit → Google Sheets
────────────────────────────────────
Phase 1 (historical): run locally, crawls as far back as possible
Phase 2 (daily):      run via GitHub Actions, appends last 24h (72h on Mondays)

Requirements:
    pip install gspread google-auth

Setup:
    1. Create a Google Cloud project & enable Google Sheets API + Google Drive API
    2. Create a Service Account, download credentials JSON as 'credentials.json'
    3. Share your Google Sheet with the service account email
    4. Set SHEET_ID to your Google Sheet ID (from the URL)
"""

import urllib.request
import urllib.error
import xml.etree.ElementTree as ET
import re
import os
import time
import json
from datetime import datetime, timezone

try:
    import gspread
    from google.oauth2.service_account import Credentials
except ImportError:
    print("Missing dependencies. Run: pip install gspread google-auth")
    exit(1)

# ── CONFIG ────────────────────────────────────────────────────────────────────
SUBREDDITS       = ["RoverPetSitting"]
SHEET_ID         = os.environ.get("SHEET_ID", "YOUR_GOOGLE_SHEET_ID_HERE")
CREDS_FILE       = os.environ.get("CREDS_FILE", "credentials.json")
HISTORICAL_MODE  = os.environ.get("HISTORICAL_MODE", "false").lower() == "true"
MAX_POSTS        = 100
# ─────────────────────────────────────────────────────────────────────────────

# ── TAXONOMY (built from your internal CSV) ───────────────────────────────────
THEMES = {
    "Availability": [
        "lead time", "overlap", "overlaps", "buffer time", "route optimization",
        "working hours", "date range", "bookings visibility", "calendar", "min stay",
        "max stay", "time of day", "capacity", "schedule", "availability",
        "calendar sync", "time off", "days off", "block off",
    ],
    "Business": [
        "joining rover", "new to rover", "search rank", "pricing strategy",
        "star sitter", "pricing transparency", "service structure", "high quality",
        "self promotion", "cancellation", "star rating", "review", "low demand",
        "business insurance", "full time", "part time", "shared account", "team",
        "profile", "backup", "income", "earnings", "worth it", "profitable",
    ],
    "Clients": [
        "dropping client", "drop a client", "block client", "difficult client",
        "bad client", "locked rate", "off platform", "off-platform", "off app",
        "centralize", "client management", "repeat client", "new client",
    ],
    "Communication": [
        "media upload", "video call", "saved response", "template response",
        "archive conversation", "auto-correct", "autocorrect", "crm",
        "notification", "reminder", "messaging", "inbox", "chat", "message",
        "flag client", "communication",
    ],
    "Diversion": [
        "going off app", "off app", "off platform", "direct payment",
        "venmo", "zelle", "paypal", "bypass rover", "diversion",
    ],
    "Experience": [
        "app parity", "web parity", "glitch", "lag", "bug", "crash",
        "navigation", "user friendly", "ux", "ui", "interface", "broken",
        "not working", "slow", "freeze", "error", "app is",
    ],
    "Payments": [
        "faster payment", "payout", "pay out", "refund", "upfront payment",
        "tip", "tipping", "expense", "reimburs", "direct deposit", "payment",
        "get paid", "waiting to be paid",
    ],
    "Preferences and rates": [
        "additional pet", "extra pet", "breed", "puppy", "puppies",
        "discount", "promo", "cats", "kittens", "short lead", "last minute",
        "dog size", "large dog", "small dog", "holiday rate", "constant care",
        "other pets", "base rate", "senior dog", "pick up", "drop off",
        "late fee", "energy level", "meet and greet", "m&g", "weekend rate",
        "hourly", "distance", "special needs", "recurring booking",
        "extended stay", "automated rate",
    ],
    "Recurring billings": [
        "recurring", "frequency", "customize schedule", "ending relationship",
        "payment issue", "skip unit", "cancellation policy", "subscription",
        "repeat booking", "auto charge",
    ],
    "Requests": [
        "intake form", "questionnaire", "contract", "referring sitter",
        "against preference", "pet profile", "owner profile", "trial",
        "archive request", "cms", "customize request", "wrong request",
        "irrelevant request",
    ],
    "Rover Cards": [
        "rover card", "rover cards", "gps", "live update", "offline",
        "sending video", "overnight card", "forgot to start", "forgot to end",
        "customization", "mandatory card", "optional card", "card glitch",
    ],
    "Rover fees": [
        "20%", "20 percent", "rover fee", "rover's fee", "rover cut",
        "service fee", "owner fee", "owner side fee", "entrance fee",
        "commission", "platform fee", "take too much",
    ],
    "Taxes": [
        "tax", "taxes", "1099", "mileage", "business expense",
        "tax info", "financial adviser", "deduction", "write off",
    ],
}


def tag_post(title: str, text: str) -> list[str]:
    """Return all matching themes for a post based on keyword rules."""
    combined = (title + " " + text).lower()
    matched = []
    for theme, keywords in THEMES.items():
        for kw in keywords:
            if kw in combined:
                matched.append(theme)
                break  # one match per theme is enough
    return matched if matched else ["Untagged"]


def strip_html(text: str) -> str:
    clean = re.sub(r"<[^>]+>", "", text)
    clean = re.sub(r"\[link\].*", "", clean)
    return clean.strip()


def fetch_rss(subreddit: str, after_ts: float = 0) -> list[dict]:
    """Fetch posts via Reddit RSS. Returns posts newer than after_ts."""
    url = f"https://www.reddit.com/r/{subreddit}/new/.rss?limit={MAX_POSTS}"
    headers = {
        "User-Agent": "Mozilla/5.0 (compatible; rover-sheet/1.0)",
        "Accept":     "application/rss+xml, application/xml, text/xml",
    }
    req = urllib.request.Request(url, headers=headers)
    NS = {"atom": "http://www.w3.org/2005/Atom"}

    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            raw = resp.read().decode("utf-8", errors="replace")
        root = ET.fromstring(raw)
        entries = root.findall("atom:entry", NS)

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

            tags = tag_post(title, content)

            posts.append({
                "date":     datetime.fromtimestamp(created_utc, tz=timezone.utc).strftime("%Y-%m-%d %H:%M UTC"),
                "title":    title,
                "url":      url_val,
                "author":   author.replace("/u/", ""),
                "preview":  content[:500],
                "tags":     ", ".join(tags),
                "ts":       created_utc,
            })

        posts.sort(key=lambda x: x["ts"])
        return posts

    except Exception as e:
        print(f"  Error fetching r/{subreddit}: {e}")
        return []


def get_sheet():
    """Authenticate and return the worksheet."""
    scopes = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive",
    ]
    # Support credentials as env var (for GitHub Actions) or file (local)
    creds_json = os.environ.get("GOOGLE_CREDS_JSON")
    if creds_json:
        creds_dict = json.loads(creds_json)
        creds = Credentials.from_service_account_info(creds_dict, scopes=scopes)
    else:
        creds = Credentials.from_service_account_file(CREDS_FILE, scopes=scopes)

    client = gspread.authorize(creds)
    sheet  = client.open_by_key(SHEET_ID)

    # Use or create a worksheet called "Reddit Posts"
    try:
        ws = sheet.worksheet("Reddit Posts")
    except gspread.exceptions.WorksheetNotFound:
        ws = sheet.add_worksheet(title="Reddit Posts", rows=5000, cols=10)
        # Write header row
        ws.append_row(["Date", "Title", "URL", "Author", "Preview", "Themes", "Subreddit"])
        # Format header bold
        ws.format("A1:G1", {"textFormat": {"bold": True}})
    return ws


def get_latest_timestamp(ws) -> float:
    """Find the most recent post timestamp already in the sheet."""
    all_dates = ws.col_values(1)[1:]  # skip header
    if not all_dates:
        return 0.0
    latest = ""
    for d in all_dates:
        if d > latest:
            latest = d
    if not latest:
        return 0.0
    try:
        dt = datetime.strptime(latest, "%Y-%m-%d %H:%M UTC").replace(tzinfo=timezone.utc)
        return dt.timestamp()
    except Exception:
        return 0.0


def append_posts(ws, posts: list[dict], subreddit: str):
    """Append new posts to the sheet in bulk."""
    if not posts:
        print("  No new posts to append.")
        return
    rows = [
        [p["date"], p["title"], p["url"], p["author"], p["preview"], p["tags"], subreddit]
        for p in posts
    ]
    ws.append_rows(rows, value_input_option="RAW")
    print(f"  ✅ Appended {len(rows)} posts to sheet.")


def main():
    print("Connecting to Google Sheets...")
    ws = get_sheet()

    if HISTORICAL_MODE:
        print("📚 HISTORICAL MODE — fetching all available posts (no time filter)")
        after_ts = 0.0
    else:
        # Daily mode: only fetch posts newer than what's already in the sheet
        after_ts = get_latest_timestamp(ws)
        if after_ts:
            print(f"📅 DAILY MODE — fetching posts newer than {datetime.fromtimestamp(after_ts, tz=timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}")
        else:
            print("📅 DAILY MODE — sheet is empty, fetching all available posts")

    for sub in SUBREDDITS:
        print(f"\nFetching r/{sub}...")
        posts = fetch_rss(sub, after_ts=after_ts)
        print(f"  Found {len(posts)} new posts")
        append_posts(ws, posts, sub)

    print("\nDone!")


if __name__ == "__main__":
    main()
