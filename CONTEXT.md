# Rover Sitter Monitor — System Context

## What this is
A daily automated pipeline that monitors r/RoverPetSitting and:
1. Sends an HTML email digest every morning at 9AM CET
2. Appends new posts to a Google Sheet with theme/problem tags

## Files
| File | Purpose |
|------|---------|
| `rover_monitor.py` | Fetches posts, builds HTML email, sends via Gmail SMTP |
| `rover_sheet_dump.py` | Fetches posts, tags them, appends to Google Sheet |
| `.github/workflows/daily_digest.yml` | GitHub Actions — runs both scripts daily |

## Infrastructure
- **Hosting**: GitHub Actions (free tier), runs daily at 08:00 UTC (09:00 CET)
- **Email**: Gmail SMTP via App Password
- **Sheet**: Google Sheets via Service Account (gspread)
- **Data source**: Arctic Shift API (primary), Reddit RSS (fallback)

## Environment variables / GitHub Secrets
| Secret | Used by | Value |
|--------|---------|-------|
| `GMAIL_SENDER` | rover_monitor.py | Gmail address (sender) |
| `GMAIL_APP_PASS` | rover_monitor.py | 16-char Gmail App Password |
| `SHEET_ID` | rover_sheet_dump.py | Google Sheet ID from URL |
| `GOOGLE_CREDS_JSON` | rover_sheet_dump.py | Full contents of credentials.json |

## Data sources
### Arctic Shift (primary)
- URL: `https://arctic-shift.photon-reddit.com/api/posts/search`
- Key params: `subreddit`, `limit` (max 100), `sort=desc` for latest posts; `after` (ISO date) for pagination
- Returns JSON: `{ "data": [ { "title", "selftext", "permalink", "author", "created_utc", "score", "num_comments", "thumbnail" } ] }`
- `created_utc` can be int or string — always cast to int
- No auth needed, no bot blocking, free

### Reddit RSS (fallback)
- URL: `https://www.reddit.com/r/{subreddit}/new/.rss?limit=100`
- Returns Atom XML — parse with `xml.etree.ElementTree`
- Namespace: `{"atom": "http://www.w3.org/2005/Atom"}`
- Often returns 403 from cloud IPs (GitHub Actions) — use Arctic Shift first

## Email script logic (rover_monitor.py)
- Fetches posts from the last **24h**, always (no Monday special case)
- Sends HTML email via `smtplib.SMTP_SSL("smtp.gmail.com", 465)`
- Recipients: `RECIPIENTS` list (hardcoded) — currently `["ux@rover.com"]`
- Post dict keys: `title`, `url`, `author`, `created`, `age_hours`, `preview`, `sort_key`, `upvotes`, `comments`, `img`, `tags`
- **Thumbnails**: `thumbnail` field from Arctic Shift — skip values `self`, `default`, `nsfw`, `spoiler`; render as 140×140 image above the post title when present
- **Tags**: imported from `rover_sheet_dump.tag_post()` — problem tags rendered as gray pills after `u/username` in the meta line; posts with no matches show no pills
- Import guard: `from rover_sheet_dump import tag_post` wrapped in `try/except (ImportError, SystemExit)` so the email script still works without gspread installed

## Sheet script logic (rover_sheet_dump.py)
- **Daily mode**: reads latest timestamp from sheet col A, fetches only newer posts
- **Historical mode**: `HISTORICAL_MODE=true` env var — paginates from Jan 1 2025 to today in batches of 100
- Pagination: advance cursor to `batch[-1]["ts"] + 1` after each batch, sleep 1s between requests
- Sheet columns: `Date | Title | URL | Author | Preview | Themes | Problems | Subreddit`
- Worksheet name: `Reddit Posts`

## Tagging taxonomy (rover_sheet_dump.py)
13 themes derived from internal Rover sitter feedback:
`Availability`, `Business`, `Clients`, `Communication`, `Diversion`,
`Experience`, `Payments`, `Preferences and rates`, `Recurring billings`,
`Requests`, `Rover Cards`, `Rover fees`, `Taxes`

Each theme has ~3–10 associated problems (e.g. "20% fee", "Faster payments" under Payments).
Tagging uses keyword matching against `title + selftext` lowercased — multiple themes/problems per post allowed.
Untagged posts get `["Untagged"]`.

## GitHub Actions workflow
- Trigger: daily cron `0 8 * * *` + manual `workflow_dispatch`
- Manual inputs:
  - `historical` (yes/no) — runs sheet dump in historical mode
  - `email_only` (yes/no) — skips both sheet steps, only sends email (useful for testing)
- Steps: checkout → setup Python 3.11 → pip install gspread google-auth → run email script → run sheet script

## Known issues & fixes applied
| Issue | Fix |
|-------|-----|
| Reddit JSON API returns 403 from GitHub IPs | Switched to RSS, then Arctic Shift |
| Reddit RSS returns 403 from GitHub IPs intermittently | Arctic Shift as primary, RSS as fallback |
| Arctic Shift `sort` param — invalid values `created_utc` / `order=desc` | Use `sort=desc` for latest; `sort=asc` + `after=<ISO date>` for pagination |
| Arctic Shift expects ISO dates not Unix timestamps (sheet script) | Format with `strftime("%Y-%m-%dT%H:%M:%SZ")` |
| Python 3.9 on local Mac — no `list[dict] \| None` syntax | Removed type hints for 3.9 compat |
| Historical dump only fetched 1 batch | Fixed pagination loop in main() |

## Common iteration tasks
**Add a new subreddit**: add to `SUBREDDITS` list in both scripts
**Change time window**: edit `hours_limit` in `_parse_posts()` in rover_monitor.py (currently 24h)
**Add a keyword/theme**: add to `PROBLEMS` dict and `PROBLEM_TO_THEME` map in rover_sheet_dump.py
**Change historical start date**: edit `cursor = 1735689600` in main() of rover_sheet_dump.py (Jan 1 2025)
**Change email schedule**: edit cron in daily_digest.yml (`0 8 * * *` = 08:00 UTC = 09:00 CET)
**Test email only**: trigger workflow manually with `email_only=yes`
