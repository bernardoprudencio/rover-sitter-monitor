import urllib.request
import urllib.error
import urllib.parse
import xml.etree.ElementTree as ET
import json
import re
import smtplib
import ssl
import os
import time
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime

try:
    from rover_sheet_dump import tag_post
except (ImportError, SystemExit):
    def tag_post(title, text):
        return [], []

# ── CONFIG ────────────────────────────────────────────────────────────────────
SUBREDDITS   = ["RoverPetSitting"]
GMAIL_SENDER = os.environ["GMAIL_SENDER"]    # your Gmail address
GMAIL_PASS   = os.environ["GMAIL_APP_PASS"]  # Gmail App Password
RECIPIENT    = os.environ["GMAIL_SENDER"]
MAX_POSTS    = 100                           # posts to fetch
# ─────────────────────────────────────────────────────────────────────────────

# RSS namespaces used by Reddit
NS = {
    "atom":    "http://www.w3.org/2005/Atom",
    "media":   "http://search.yahoo.com/mrss/",
}


def _parse_posts(raw_posts: list[dict], source: str) -> list[dict]:
    """Normalise a list of raw post dicts into the internal format and apply time filter."""
    hours_limit = 24

    posts = []
    for p in raw_posts:
        created_utc = float(p.get("created_utc", time.time()))
        age_hours = (time.time() - created_utc) / 3600
        if age_hours > hours_limit:
            continue

        permalink = p.get("permalink", "")
        url_val = p.get("url") or (f"https://www.reddit.com{permalink}" if permalink else "")
        selftext = p.get("selftext", "") or ""
        clean_content = re.sub(r"<[^>]+>", "", selftext).strip()

        # Thumbnail: skip non-image placeholder values
        thumb = p.get("thumbnail", "") or ""
        img = thumb if thumb and thumb not in ("self", "default", "nsfw", "spoiler", "") else None

        # Tags from taxonomy
        title = p.get("title", "(no title)")
        _, problems = tag_post(title, clean_content)
        tags = [t for t in problems if t != "Untagged"]

        posts.append({
            "title":    title,
            "url":      url_val,
            "author":   p.get("author", "unknown"),
            "created":  datetime.fromtimestamp(created_utc, tz=timezone.utc).strftime("%b %d, %H:%M UTC"),
            "age_hours": age_hours,
            "preview":  clean_content[:300],
            "sort_key": created_utc,
            "upvotes":  p.get("score"),
            "comments": p.get("num_comments"),
            "img":      img,
            "tags":     tags,
        })

    posts.sort(key=lambda x: x["sort_key"], reverse=True)
    print(f"  Time window: {hours_limit}h")
    if posts:
        print(f"  Most recent post [{source}]: '{posts[0]['title'][:60]}' ({posts[0]['age_hours']:.1f}h ago)")
    return posts


def _fetch_arctic_shift(subreddit: str, limit: int) -> list[dict]:
    """Fetch posts from Arctic Shift API."""
    params = urllib.parse.urlencode({
        "subreddit": subreddit,
        "limit":     limit,
        "sort":      "desc",
    })
    url = f"https://arctic-shift.photon-reddit.com/api/posts/search?{params}"
    req = urllib.request.Request(url, headers={"User-Agent": "rover-monitor/1.0"})
    with urllib.request.urlopen(req, timeout=20) as resp:
        data = json.loads(resp.read().decode("utf-8"))
    raw = data.get("data", [])
    print(f"  Arctic Shift fetch OK — {len(raw)} posts received")
    return raw


def _fetch_rss_fallback(subreddit: str, limit: int) -> list[dict]:
    """Fetch posts via Reddit RSS (fallback)."""
    url = f"https://www.reddit.com/r/{subreddit}/new/.rss?limit={limit}"
    headers = {
        "User-Agent": "Mozilla/5.0 (compatible; rover-monitor/1.0)",
        "Accept":     "application/rss+xml, application/xml, text/xml",
    }
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=15) as resp:
        raw_xml = resp.read().decode("utf-8", errors="replace")
    print(f"  RSS fallback fetch OK — {len(raw_xml)} bytes received")

    root = ET.fromstring(raw_xml)
    entries = root.findall("atom:entry", NS)
    print(f"  Found {len(entries)} entries in RSS feed")

    posts = []
    for entry in entries:
        title   = entry.findtext("atom:title", default="(no title)", namespaces=NS)
        link_el = entry.find("atom:link", NS)
        url_val = link_el.get("href", "") if link_el is not None else ""
        author  = entry.findtext("atom:author/atom:name", default="unknown", namespaces=NS)
        updated = entry.findtext("atom:updated", default="", namespaces=NS)
        content = entry.findtext("atom:content", default="", namespaces=NS)

        try:
            dt = datetime.fromisoformat(updated.replace("Z", "+00:00"))
            created_utc = dt.timestamp()
        except Exception:
            created_utc = time.time()

        clean_content = re.sub(r"<[^>]+>", "", content).strip()
        clean_content = re.sub(r"\[link\].*", "", clean_content).strip()

        posts.append({
            "title":       title,
            "url":         url_val,
            "author":      author.replace("/u/", ""),
            "created_utc": created_utc,
            "selftext":    clean_content,
            "score":        None,
            "num_comments": None,
            "thumbnail":    None,
            "tags":         [],
        })
    return posts


def fetch_posts(subreddit: str) -> list[dict]:
    """Fetch posts — Arctic Shift API primary, Reddit RSS fallback."""
    limit = MAX_POSTS

    # ── Primary: Arctic Shift ──────────────────────────────────────────────
    try:
        raw = _fetch_arctic_shift(subreddit, limit)
        return _parse_posts(raw, "Arctic Shift")
    except Exception as e:
        print(f"  Arctic Shift error ({e}), falling back to RSS...")

    # ── Fallback: Reddit RSS ───────────────────────────────────────────────
    try:
        raw = _fetch_rss_fallback(subreddit, limit)
        return _parse_posts(raw, "RSS fallback")
    except urllib.error.HTTPError as e:
        print(f"  RSS HTTP error: {e.code} {e.reason}")
    except ET.ParseError as e:
        print(f"  RSS XML parse error: {e}")
    except Exception as e:
        print(f"  RSS unexpected error: {e}")

    return []


def build_html(posts_by_sub: dict) -> str:
    """Render a clean HTML email."""
    today = datetime.now().strftime("%B %d, %Y")
    total = sum(len(v) for v in posts_by_sub.values())

    rows = ""
    for subreddit, posts in posts_by_sub.items():
        if not posts:
            continue
        rows += f"""
        <tr>
          <td style="padding:20px 0 8px;font-size:18px;font-weight:bold;
              color:#FF5700;border-bottom:2px solid #FF5700;">
            r/{subreddit}
          </td>
        </tr>"""
        for p in posts:
            age_str = f"{p['age_hours']:.0f}h ago" if p['age_hours'] < 48 else p['created']
            tags_html = "".join(
                f'<span style="display:inline-block;background:#f0f0f0;color:#555;'
                f'font-size:11px;padding:2px 7px;border-radius:10px;margin-right:4px;">{t}</span>'
                for t in p.get("tags", [])
            )
            meta = f"🕐 {age_str} &nbsp;·&nbsp; u/{p['author']} &nbsp;{tags_html}"
            img_html = (
                f'<div style="margin-bottom:10px;">'
                f'<a href="{p["url"]}"><img src="{p["img"]}" alt="" width="140" height="140" '
                f'style="border-radius:6px;object-fit:cover;display:block;"></a></div>'
            ) if p.get("img") else ""
            rows += f"""
        <tr>
          <td style="padding:16px 0;border-bottom:1px solid #eee;vertical-align:top;">
            {img_html}<div style="font-size:15px;font-weight:600;margin-bottom:6px;">
              <a href="{p['url']}" style="color:#1a1a1a;text-decoration:none;">{p['title']}</a>
            </div>
            <div style="color:#555;font-size:13px;line-height:1.5;margin-bottom:8px;">
              {p['preview']}{'...' if len(p['preview']) == 300 else ''}
            </div>
            <div style="font-size:12px;color:#999;">{meta}</div>
          </td>
        </tr>"""

    if not rows:
        rows = """<tr><td style="padding:20px;color:#999;text-align:center;">
            No posts found.</td></tr>"""

    return f"""<!DOCTYPE html>
<html>
<head><meta charset="UTF-8"></head>
<body style="margin:0;padding:0;background:#f5f5f5;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;">
  <table width="100%" cellpadding="0" cellspacing="0" style="background:#f5f5f5;padding:30px 0;">
    <tr><td align="center">
      <table width="620" cellpadding="0" cellspacing="0"
             style="background:#fff;border-radius:8px;overflow:hidden;box-shadow:0 2px 8px rgba(0,0,0,.08);">
        <tr>
          <td style="background:#FF5700;padding:24px 32px;">
            <div style="font-size:22px;font-weight:700;color:#fff;">🐾 Rover Sitter Pulse</div>
            <div style="color:#ffe0cc;font-size:14px;margin-top:4px;">{today} &nbsp;·&nbsp; {total} posts</div>
          </td>
        </tr>
        <tr>
          <td style="padding:0 32px 24px;">
            <table width="100%" cellpadding="0" cellspacing="0">
              {rows}
            </table>
          </td>
        </tr>
        <tr>
          <td style="background:#fafafa;padding:16px 32px;border-top:1px solid #eee;
              font-size:12px;color:#aaa;text-align:center;">
            Rover Sitter Monitor · r/RoverPetSitting
          </td>
        </tr>
      </table>
    </td></tr>
  </table>
</body>
</html>"""


def send_email(html: str, total: int):
    """Send the digest via Gmail SMTP."""
    today = datetime.now().strftime("%B %d, %Y")
    msg = MIMEMultipart("alternative")
    msg["Subject"] = f"🐾 Rover Sitter Pulse — {today} ({total} posts)"
    msg["From"]    = GMAIL_SENDER
    msg["To"]      = RECIPIENT
    msg.attach(MIMEText(html, "html"))

    ctx = ssl.create_default_context()
    with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=ctx) as server:
        server.login(GMAIL_SENDER, GMAIL_PASS)
        server.sendmail(GMAIL_SENDER, RECIPIENT, msg.as_string())
    print(f"✅ Email sent to {RECIPIENT}")


def main():
    posts_by_sub = {}
    for sub in SUBREDDITS:
        print(f"\nFetching r/{sub}...")
        posts = fetch_posts(sub)
        posts_by_sub[sub] = posts
        print(f"  → {len(posts)} posts will appear in email")

    total = sum(len(v) for v in posts_by_sub.values())
    print(f"\nTotal posts: {total}")
    html = build_html(posts_by_sub)
    send_email(html, total)


if __name__ == "__main__":
    main()
