import urllib.request
import urllib.error
import xml.etree.ElementTree as ET
import smtplib
import ssl
import os
import time
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime

# ── CONFIG ────────────────────────────────────────────────────────────────────
SUBREDDITS   = ["RoverPetSitting"]
GMAIL_SENDER = os.environ["GMAIL_SENDER"]    # your Gmail address
GMAIL_PASS   = os.environ["GMAIL_APP_PASS"]  # Gmail App Password
RECIPIENT    = os.environ["GMAIL_SENDER"]    # sending to yourself
MAX_POSTS    = 50                            # posts to fetch per subreddit
# ─────────────────────────────────────────────────────────────────────────────

# RSS namespaces used by Reddit
NS = {
    "atom":    "http://www.w3.org/2005/Atom",
    "media":   "http://search.yahoo.com/mrss/",
}


def fetch_posts(subreddit: str) -> list[dict]:
    """Fetch posts via Reddit's public RSS feed (much less likely to be blocked)."""
    url = f"https://www.reddit.com/r/{subreddit}/new/.rss?limit={MAX_POSTS}"
    headers = {
        "User-Agent": "Mozilla/5.0 (compatible; rover-monitor/1.0)",
        "Accept":     "application/rss+xml, application/xml, text/xml",
    }
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            raw = resp.read().decode("utf-8", errors="replace")
        print(f"  RSS fetch OK — {len(raw)} bytes received")

        root = ET.fromstring(raw)
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

            # Parse timestamp
            try:
                dt = datetime.fromisoformat(updated.replace("Z", "+00:00"))
                created_utc = dt.timestamp()
            except Exception:
                created_utc = time.time()

            # Strip HTML tags from content crudely
            import re
            clean_content = re.sub(r"<[^>]+>", "", content).strip()
            # Remove the "submitted by" footer Reddit adds
            clean_content = re.sub(r"\[link\].*", "", clean_content).strip()

            age_hours = (time.time() - created_utc) / 3600

            posts.append({
                "title":     title,
                "url":       url_val,
                "author":    author.replace("/u/", ""),
                "created":   datetime.fromtimestamp(created_utc, tz=timezone.utc).strftime("%b %d, %H:%M UTC"),
                "age_hours": age_hours,
                "preview":   clean_content[:300],
                "sort_key":  created_utc,
                # RSS doesn't give upvotes/comments so we'll omit them
                "upvotes":   None,
                "comments":  None,
            })

        posts.sort(key=lambda x: x["sort_key"], reverse=True)
        if posts:
            print(f"  Most recent post: '{posts[0]['title'][:60]}' ({posts[0]['age_hours']:.1f}h ago)")
        return posts

    except urllib.error.HTTPError as e:
        print(f"  HTTP error fetching r/{subreddit}: {e.code} {e.reason}")
        return []
    except ET.ParseError as e:
        print(f"  XML parse error: {e}")
        return []
    except Exception as e:
        print(f"  Unexpected error: {e}")
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
            meta = f"🕐 {age_str} &nbsp;·&nbsp; u/{p['author']}"
            rows += f"""
        <tr>
          <td style="padding:16px 0;border-bottom:1px solid #eee;vertical-align:top;">
            <div style="font-size:15px;font-weight:600;margin-bottom:6px;">
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
        print(f"\nFetching r/{sub} via RSS...")
        posts = fetch_posts(sub)
        posts_by_sub[sub] = posts
        print(f"  → {len(posts)} posts will appear in email")

    total = sum(len(v) for v in posts_by_sub.values())
    print(f"\nTotal posts: {total}")
    html = build_html(posts_by_sub)
    send_email(html, total)


if __name__ == "__main__":
    main()
