import urllib.request
import urllib.error
import json
import smtplib
import ssl
import os
import time
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime, timezone, timedelta

# ── CONFIG ────────────────────────────────────────────────────────────────────
SUBREDDITS   = ["RoverPetSitting"]
GMAIL_SENDER = os.environ["GMAIL_SENDER"]   # your Gmail address
GMAIL_PASS   = os.environ["GMAIL_APP_PASS"] # Gmail App Password (not your real password)
RECIPIENT    = os.environ["GMAIL_SENDER"]   # sending to yourself

# Keywords for scoring / tagging
CATEGORIES = {
    "🚨 Churn Signal":      ["leaving rover", "switching to wag", "quitting rover", "deleted my account",
                              "cancelling", "uninstalling", "done with rover", "last straw", "fed up"],
    "⚠️ Pain Point":        ["frustrated", "annoying", "broken", "bug", "glitch", "unfair", "scam",
                              "ripped off", "terrible", "awful", "worst", "ridiculous", "no support",
                              "ignored", "no response", "deactivated", "banned", "suspended"],
    "💡 Feature Request":   ["wish rover", "rover should", "would be nice", "feature request",
                              "please add", "why can't rover", "rover needs", "suggestion"],
    "🏆 Praise":            ["love rover", "rover is great", "amazing platform", "best app",
                              "rover saved", "highly recommend", "great experience", "so grateful"],
    "🤝 Competitor Mention":["wag", "trusted housesitters", "care.com", "pet sitter", "pet sitting app",
                              "rover vs", "vs rover"],
}

HOURS_BACK = 24  # look at last 24 hours
MAX_POSTS   = 30 # max posts to fetch per subreddit
# ─────────────────────────────────────────────────────────────────────────────


def fetch_posts(subreddit: str) -> list[dict]:
    """Fetch new posts from a subreddit using the public JSON API."""
    url = f"https://www.reddit.com/r/{subreddit}/new.json?limit={MAX_POSTS}"
    req = urllib.request.Request(url, headers={"User-Agent": "rover-monitor/1.0"})
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode())
        return [p["data"] for p in data["data"]["children"]]
    except urllib.error.HTTPError as e:
        print(f"HTTP error fetching r/{subreddit}: {e.code}")
        return []
    except Exception as e:
        print(f"Error fetching r/{subreddit}: {e}")
        return []


def score_and_tag(post: dict) -> dict | None:
    """
    Filter posts from last 24h, score them by keyword relevance,
    return enriched dict or None if not relevant enough.
    """
    cutoff = time.time() - (HOURS_BACK * 3600)
    if post.get("created_utc", 0) < cutoff:
        return None

    text = f"{post.get('title', '')} {post.get('selftext', '')}".lower()

    tags   = []
    score  = 0

    for category, keywords in CATEGORIES.items():
        for kw in keywords:
            if kw in text:
                if category not in tags:
                    tags.append(category)
                score += 1

    # Always include posts with high engagement even if no keyword match
    upvotes  = post.get("score", 0)
    comments = post.get("num_comments", 0)
    engagement_bonus = (upvotes // 10) + (comments // 5)
    score += engagement_bonus

    if score == 0:
        return None  # not relevant enough

    created = datetime.fromtimestamp(post["created_utc"], tz=timezone.utc)

    return {
        "title":    post.get("title", "(no title)"),
        "url":      f"https://reddit.com{post.get('permalink', '')}",
        "upvotes":  upvotes,
        "comments": comments,
        "tags":     tags if tags else ["📌 High Engagement"],
        "score":    score,
        "preview":  post.get("selftext", "")[:300].strip() or "(no text — link post)",
        "created":  created.strftime("%b %d, %H:%M UTC"),
        "author":   post.get("author", "unknown"),
    }


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
          <td colspan="2" style="padding:20px 0 8px;font-size:18px;font-weight:bold;
              color:#FF5700;border-bottom:2px solid #FF5700;">
            r/{subreddit}
          </td>
        </tr>"""
        for p in posts:
            tag_html = " ".join(
                f'<span style="background:#fff3e0;border:1px solid #ffb74d;border-radius:12px;'
                f'padding:2px 8px;font-size:12px;margin-right:4px;">{t}</span>'
                for t in p["tags"]
            )
            rows += f"""
        <tr>
          <td style="padding:16px 0;border-bottom:1px solid #eee;vertical-align:top;">
            <div style="font-size:15px;font-weight:600;margin-bottom:6px;">
              <a href="{p['url']}" style="color:#1a1a1a;text-decoration:none;">{p['title']}</a>
            </div>
            <div style="margin-bottom:8px;">{tag_html}</div>
            <div style="color:#555;font-size:13px;line-height:1.5;margin-bottom:8px;">
              {p['preview']}{'...' if len(p['preview']) == 300 else ''}
            </div>
            <div style="font-size:12px;color:#999;">
              ▲ {p['upvotes']} upvotes &nbsp;·&nbsp; 
              💬 {p['comments']} comments &nbsp;·&nbsp; 
              🕐 {p['created']} &nbsp;·&nbsp;
              u/{p['author']}
            </div>
          </td>
        </tr>"""

    if not rows:
        rows = """<tr><td style="padding:20px;color:#999;text-align:center;">
            No relevant posts found in the last 24 hours.</td></tr>"""

    return f"""<!DOCTYPE html>
<html>
<head><meta charset="UTF-8"></head>
<body style="margin:0;padding:0;background:#f5f5f5;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;">
  <table width="100%" cellpadding="0" cellspacing="0" style="background:#f5f5f5;padding:30px 0;">
    <tr><td align="center">
      <table width="620" cellpadding="0" cellspacing="0"
             style="background:#fff;border-radius:8px;overflow:hidden;box-shadow:0 2px 8px rgba(0,0,0,.08);">

        <!-- Header -->
        <tr>
          <td style="background:#FF5700;padding:24px 32px;">
            <div style="font-size:22px;font-weight:700;color:#fff;">🐾 Rover Sitter Pulse</div>
            <div style="color:#ffe0cc;font-size:14px;margin-top:4px;">{today} &nbsp;·&nbsp; {total} posts flagged</div>
          </td>
        </tr>

        <!-- Body -->
        <tr>
          <td style="padding:0 32px 24px;">
            <table width="100%" cellpadding="0" cellspacing="0">
              {rows}
            </table>
          </td>
        </tr>

        <!-- Footer -->
        <tr>
          <td style="background:#fafafa;padding:16px 32px;border-top:1px solid #eee;
              font-size:12px;color:#aaa;text-align:center;">
            Rover Sitter Monitor · Posts from last 24h · r/RoverPetSitting
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
        print(f"Fetching r/{sub}...")
        raw = fetch_posts(sub)
        enriched = [r for p in raw if (r := score_and_tag(p)) is not None]
        enriched.sort(key=lambda x: x["score"], reverse=True)
        posts_by_sub[sub] = enriched
        print(f"  → {len(enriched)} relevant posts found")

    total = sum(len(v) for v in posts_by_sub.values())
    html  = build_html(posts_by_sub)
    send_email(html, total)


if __name__ == "__main__":
    main()
