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

# ── TAXONOMY ──────────────────────────────────────────────────────────────────
# Each entry: "Problem name" : ["keyword1", "keyword2", ...]
# Keywords are matched against (title + post body) lowercased.
# Theme is derived from the problem → theme mapping below.

PROBLEMS = {
    # ── Availability ──────────────────────────────────────────────────────────
    "Long lead time":               ["lead time", "far ahead", "book too early", "advance booking"],
    "Overlaps":                     ["overlap", "double book", "double-book", "conflict"],
    "Buffer time":                  ["buffer time", "buffer between", "gap between booking"],
    "Route optimization":           ["route", "optimize route", "flexible times", "travel between"],
    "Working hours":                ["working hours", "outside hours", "after hours", "bother me"],
    "Date range selection":         ["date range", "select dates", "date picker"],
    "Bookings visibility":          ["bookings visibility", "see my bookings", "calendar view"],
    "Time of day":                  ["time of day", "time-of-day", "available hours", "availability window"],
    "Min/max stay":                 ["min stay", "max stay", "minimum stay", "maximum stay", "shortest booking", "longest booking"],
    "Time off / holidays":          ["time off", "vacation", "block off", "unavailable"],
    "Calendar sync":                ["calendar sync", "google calendar", "sync calendar", "ical"],
    "Capacity comprehension":       ["capacity", "how many dogs", "max dogs", "maximum dogs"],

    # ── Business ──────────────────────────────────────────────────────────────
    "Joining and starting on Rover":["joining rover", "new to rover", "just started", "starting on rover", "is rover worth"],
    "Insights":                     ["insights", "analytics", "stats", "impact of preferences", "data"],
    "Search rank":                  ["search rank", "search ranking", "appear in search", "visibility in search", "ranking"],
    "Pricing strategy":             ["pricing strategy", "how to price", "set my prices", "what to charge"],
    "Star Sitter":                  ["star sitter", "top sitter", "elite sitter", "sitter badge"],
    "Pricing transparency":         ["pricing transparency", "upfront cost", "show fees", "full price", "hidden fee"],
    "Service structure":            ["service structure", "service type", "service offering"],
    "High quality pet care":        ["high quality", "better care", "improve care", "courses", "training", "certification"],
    "Self promotion":               ["self promot", "promote myself", "advertise", "social media", "flyer", "neighborhood"],
    "Cancellations":                ["cancellation", "cancel", "cancelled booking", "cancellation policy"],
    "Star ratings and reviews":     ["star rating", "review", "rating", "stars", "review system"],
    "Low demand":                   ["low demand", "no bookings", "slow", "not enough clients", "more clients"],
    "Business insurance":           ["insurance", "liability", "covered", "protect"],
    "Part/full-time":               ["full time", "full-time", "part time", "part-time", "grow my business"],
    "Shared accounts / teams":      ["shared account", "partner account", "team account", "share account"],
    "Profile customization":        ["profile", "website", "customize profile", "profile page"],
    "Reports":                      ["report", "earnings report", "working hours report", "summary"],

    # ── Clients ───────────────────────────────────────────────────────────────
    "Dropping clients":             ["drop a client", "dropping client", "fire a client", "block client", "stop working with"],
    "Centralize on clients":        ["centralize", "client management", "manage clients", "client list"],
    "Locked rates":                 ["locked rate", "lock rate", "rate locked", "can't change rate"],
    "Off-platform management":      ["off platform", "off-platform", "outside rover", "manage off app"],

    # ── Communication ─────────────────────────────────────────────────────────
    "Media uploads":                ["media upload", "upload photo", "upload video", "send photo", "send video", "attach"],
    "Video calls":                  ["video call", "video chat", "facetime", "zoom"],
    "Custom/saved responses":       ["saved response", "template message", "canned response", "quick reply"],
    "Archiving conversations":      ["archive conversation", "archive chat", "archive message"],
    "Auto-correct":                 ["auto-correct", "autocorrect", "autocomplete"],
    "Functionality":                ["reactions", "unsend", "search inbox", "live messaging", "timezone"],
    "Reminders":                    ["reminder", "remind me", "notification reminder"],
    "Flag repeat clients":          ["repeat client", "previous client", "returning client", "flag client"],

    # ── Diversion ─────────────────────────────────────────────────────────────
    "Going off app":                ["off app", "off platform", "venmo", "zelle", "paypal", "cash", "bypass rover", "direct payment", "going direct"],

    # ── Experience ────────────────────────────────────────────────────────────
    "Web / app parity":             ["web parity", "app parity", "desktop version", "mobile version", "web vs app"],
    "Glitches / lag / bugs":        ["glitch", "lag", "bug", "crash", "not working", "broken", "freeze", "error", "slow app"],
    "Navigation":                   ["navigation", "navigate", "can't find", "hard to find", "confusing"],
    "User friendly":                ["user friendly", "user-friendly", "intuitive", "easy to use", "complicated"],

    # ── Payments ──────────────────────────────────────────────────────────────
    "Faster payments":              ["faster payment", "payout speed", "waiting to get paid", "payment delay", "slow payout", "when do i get paid"],
    "Refunds":                      ["refund", "reimburse", "money back"],
    "Paying upfront":               ["pay upfront", "upfront payment", "payment method", "pay before"],
    "Tipping":                      ["tip", "tipping", "gratuity"],
    "Expenses":                     ["expense", "out of pocket", "vet bill", "reimburse expense"],

    # ── Preferences and rates ─────────────────────────────────────────────────
    "Additional pets":              ["additional pet", "extra pet", "multiple pets", "second dog", "add a pet"],
    "Extended stay":                ["extended stay", "long stay", "longer booking", "price after"],
    "Breeds":                       ["breed", "pit bull", "pitbull", "aggressive breed", "restricted breed", "dangerous breed"],
    "New/repeat clients":           ["new client rate", "repeat client rate", "returning client rate"],
    "Discounts / promos":           ["discount", "promo", "coupon", "deal", "promo code"],
    "Puppies":                      ["puppy", "puppies", "young dog"],
    "Cats and kittens":             ["cat", "kitten", "feline"],
    "Short lead time":              ["short lead", "last minute", "same day", "last-minute fee"],
    "Dog sizes":                    ["dog size", "large dog", "small dog", "weight limit", "size limit", "big dog"],
    "Holidays":                     ["holiday rate", "holiday pricing", "christmas", "thanksgiving", "holiday surcharge"],
    "Constant care":                ["constant care", "24/7", "around the clock", "all day care"],
    "Other pets":                   ["other pets", "exotic", "rabbit", "bird", "reptile", "small animal"],
    "Senior dogs":                  ["senior dog", "old dog", "elderly dog", "geriatric"],
    "Pick-up and drop-off":         ["pick up", "drop off", "pickup", "dropoff", "key pickup"],
    "Late fees":                    ["late fee", "late pickup", "picked up late", "overtime charge"],
    "Energy level":                 ["energy level", "high energy", "hyperactive", "energetic dog"],
    "Meet and Greet":               ["meet and greet", "m&g", "meet greet", "trial meeting"],
    "Recurring bookings":           ["recurring booking", "recurring service", "regular booking"],
    "Special needs":                ["special needs", "disabled pet", "medical needs", "medication"],
    "Hourly":                       ["hourly rate", "charge by hour", "hourly"],
    "Weekend":                      ["weekend rate", "weekend pricing", "weekend surcharge"],
    "Distance":                     ["distance", "travel distance", "how far", "service area"],
    "Base rate":                    ["base rate", "base price", "starting rate", "minimum rate"],
    "Automated rates":              ["automated rate", "dynamic pricing", "auto rate", "automatic pricing"],

    # ── Recurring billings ────────────────────────────────────────────────────
    "Customize schedule":           ["customize schedule", "modify schedule", "change schedule", "update recurring"],
    "Ending a relationship":        ["end relationship", "ending relationship", "cancel recurring", "stop recurring", "end recurring"],
    "Skipping units":               ["skip unit", "skipping unit", "missed unit", "skip a session"],
    "Customize units":              ["customize unit", "update unit", "change unit", "modify unit"],
    "Cancellation policies":        ["cancellation policy", "cancel policy", "recurring cancellation"],
    "Payment issues":               ["payment issue", "payment problem", "charge failed", "billing issue"],

    # ── Requests ──────────────────────────────────────────────────────────────
    "Intake form":                  ["intake form", "questionnaire", "booking questions", "pre-booking form"],
    "CMS":                          ["wrong request", "irrelevant request", "not meant for me", "cms"],
    "Customize request":            ["customize request", "custom request", "request details"],
    "Trial":                        ["trial", "trial stay", "trial walk", "trial booking", "test booking"],
    "Against preference":           ["against preference", "outside preference", "strict preference", "ignore preference"],
    "Referring other sitters":      ["refer sitter", "referring sitter", "recommend sitter", "backup sitter"],
    "Contracts":                    ["contract", "agreement", "liability waiver", "waiver"],

    # ── Rover Cards ───────────────────────────────────────────────────────────
    "Sending videos":               ["send video", "video on rover card", "rover card video"],
    "Live updates":                 ["live update", "real time update", "update during service"],
    "Offline support":              ["offline", "no internet", "no signal", "no connection"],
    "GPS accuracy":                 ["gps", "gps accuracy", "wrong distance", "tracking"],
    "Forgot to start or end it":    ["forgot to start", "forgot to end", "forgot to check in", "forgot to check out"],
    "Glitches and bugs (Cards)":    ["rover card glitch", "rover card bug", "card not working", "card error"],
    "Mandatory / optional":         ["mandatory card", "optional card", "require card", "skip card"],

    # ── Rover fees ────────────────────────────────────────────────────────────
    "20% fee":                      ["20%", "20 percent", "rover's cut", "rover cut", "platform fee", "commission", "take too much", "fee is too high"],
    "Owner-side fee":               ["owner fee", "owner side fee", "owner-side fee", "pet parent fee"],
    "Entrance fee":                 ["entrance fee", "joining fee", "cost to join"],

    # ── Taxes ─────────────────────────────────────────────────────────────────
    "Track mileage":                ["mileage", "track miles", "miles driven", "odometer"],
    "1099 / tax info":              ["1099", "tax form", "tax info", "tax document"],
    "Business expenses":            ["business expense", "write off", "tax deduction", "deductible"],
    "Financial adviser":            ["financial adviser", "financial advisor", "accountant", "tax help"],
}

# Map each problem to its theme
PROBLEM_TO_THEME = {
    "Long lead time": "Availability", "Overlaps": "Availability",
    "Buffer time": "Availability", "Route optimization": "Availability",
    "Working hours": "Availability", "Date range selection": "Availability",
    "Bookings visibility": "Availability", "Time of day": "Availability",
    "Min/max stay": "Availability", "Time off / holidays": "Availability",
    "Calendar sync": "Availability", "Capacity comprehension": "Availability",
    "Joining and starting on Rover": "Business", "Insights": "Business",
    "Search rank": "Business", "Pricing strategy": "Business",
    "Star Sitter": "Business", "Pricing transparency": "Business",
    "Service structure": "Business", "High quality pet care": "Business",
    "Self promotion": "Business", "Cancellations": "Business",
    "Star ratings and reviews": "Business", "Low demand": "Business",
    "Business insurance": "Business", "Part/full-time": "Business",
    "Shared accounts / teams": "Business", "Profile customization": "Business",
    "Reports": "Business",
    "Dropping clients": "Clients", "Centralize on clients": "Clients",
    "Locked rates": "Clients", "Off-platform management": "Clients",
    "Media uploads": "Communication", "Video calls": "Communication",
    "Custom/saved responses": "Communication", "Archiving conversations": "Communication",
    "Auto-correct": "Communication", "Functionality": "Communication",
    "Reminders": "Communication", "Flag repeat clients": "Communication",
    "Going off app": "Diversion",
    "Web / app parity": "Experience", "Glitches / lag / bugs": "Experience",
    "Navigation": "Experience", "User friendly": "Experience",
    "Faster payments": "Payments", "Refunds": "Payments",
    "Paying upfront": "Payments", "Tipping": "Payments", "Expenses": "Payments",
    "Additional pets": "Preferences and rates", "Extended stay": "Preferences and rates",
    "Breeds": "Preferences and rates", "New/repeat clients": "Preferences and rates",
    "Discounts / promos": "Preferences and rates", "Puppies": "Preferences and rates",
    "Cats and kittens": "Preferences and rates", "Short lead time": "Preferences and rates",
    "Dog sizes": "Preferences and rates", "Holidays": "Preferences and rates",
    "Constant care": "Preferences and rates", "Other pets": "Preferences and rates",
    "Senior dogs": "Preferences and rates", "Pick-up and drop-off": "Preferences and rates",
    "Late fees": "Preferences and rates", "Energy level": "Preferences and rates",
    "Meet and Greet": "Preferences and rates", "Recurring bookings": "Preferences and rates",
    "Special needs": "Preferences and rates", "Hourly": "Preferences and rates",
    "Weekend": "Preferences and rates", "Distance": "Preferences and rates",
    "Base rate": "Preferences and rates", "Automated rates": "Preferences and rates",
    "Customize schedule": "Recurring billings", "Ending a relationship": "Recurring billings",
    "Skipping units": "Recurring billings", "Customize units": "Recurring billings",
    "Cancellation policies": "Recurring billings", "Payment issues": "Recurring billings",
    "Intake form": "Requests", "CMS": "Requests",
    "Customize request": "Requests", "Trial": "Requests",
    "Against preference": "Requests", "Referring other sitters": "Requests",
    "Contracts": "Requests",
    "Sending videos": "Rover Cards", "Live updates": "Rover Cards",
    "Offline support": "Rover Cards", "GPS accuracy": "Rover Cards",
    "Forgot to start or end it": "Rover Cards", "Glitches and bugs (Cards)": "Rover Cards",
    "Mandatory / optional": "Rover Cards",
    "20% fee": "Rover fees", "Owner-side fee": "Rover fees", "Entrance fee": "Rover fees",
    "Track mileage": "Taxes", "1099 / tax info": "Taxes",
    "Business expenses": "Taxes", "Financial adviser": "Taxes",
}


def tag_post(title: str, text: str) -> tuple[list[str], list[str]]:
    """Return (matched_themes, matched_problems) for a post."""
    combined = (title + " " + text).lower()
    matched_problems = []
    matched_themes   = []

    for problem, keywords in PROBLEMS.items():
        for kw in keywords:
            if kw in combined:
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
    after_param = int(after_ts) if after_ts > 1000000000 else 1714521600  # default: Jan 1 2025
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
    print("Connecting to Google Sheets...")
    ws = get_sheet()

    if HISTORICAL_MODE:
        print("📚 HISTORICAL MODE — fetching all available posts")
        after_ts = 0.0
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
