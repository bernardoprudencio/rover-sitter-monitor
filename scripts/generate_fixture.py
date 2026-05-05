#!/usr/bin/env python3
"""Generate a synthetic fixture dataset shaped like the real export.

Useful for dashboard development without hitting the live Google Sheet.
Uses tag_post() / PROBLEMS from rover_sheet_dump so the fixture shares the
same taxonomy as production.

CLI:
    python3 scripts/generate_fixture.py --out dashboard/public/data --count 200 --seed 42
"""
from __future__ import annotations

import argparse
import hashlib
import os
import random
import sys
from datetime import datetime, timedelta, timezone

# Make the repo root importable so we can pull in rover_sheet_dump + rover_export_json.
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Stub gspread/google.oauth2 if missing — fixture generation never touches the
# network. Real envs (CI / live export) have these installed for real.
try:
    import gspread  # noqa: F401
except ImportError:
    import types as _t
    _g = _t.ModuleType("gspread"); _g.exceptions = _t.SimpleNamespace(WorksheetNotFound=Exception)
    _sa = _t.ModuleType("google.oauth2.service_account")
    _sa.Credentials = type("C", (), {"from_service_account_info": staticmethod(lambda *a, **k: None),
                                     "from_service_account_file": staticmethod(lambda *a, **k: None)})
    sys.modules.update({"gspread": _g, "google": _t.ModuleType("google"),
                        "google.oauth2": _t.ModuleType("google.oauth2"),
                        "google.oauth2.service_account": _sa})

from rover_sheet_dump import PROBLEMS, tag_post  # noqa: E402
from rover_export_json import load_taxonomy, truncate_preview, write_dataset  # noqa: E402

# Templates seeded with real taxonomy keywords so tag_post() actually fires.
TITLES = [
    "Got a new puppy today, any tips?",
    "GPS is wrong on rover card again",
    "Need help with 1099 form for last year",
    "Anyone use pet insurance for liability?",
    "20% fee is too high — thinking of going off platform",
    "How do you handle a last minute booking?",
    "Holiday rate question — what's standard?",
    "Refund policy after a cancelled booking?",
    "Calendar sync with google calendar broken",
    "Forgot to start the rover card on a walk",
    "Dropping a client — what's the etiquette?",
    "Senior dog with medication — how to price?",
    "Meet and greet went sideways",
    "Search ranking dropped overnight, why?",
    "Pricing strategy for new client rate?",
    "Faster payments — when do I get paid?",
    "Tipping disabled on my profile?",
    "Recurring booking cancellation policy unclear",
    "Glitch on the app — can't see my bookings",
    "Track miles for tax deduction help",
    "Star sitter requirements changed?",
    "Cat owner asking about cats and kittens rate",
    "Large dog over weight limit — turn down?",
    "Video call before booking — anyone do this?",
    "Hourly rate vs flat rate for drop ins",
    "Saved response template ideas?",
    "Just saying hi to the community",  # untagged-ish
    "What's everyone up to this weekend?",  # untagged-ish
    "Best treats for training?",  # untagged-ish
    "Long lead time bookings — how far ahead?",
    "Distance — service area limits?",
    "Owner side fee surprise at checkout",
    "Background check question",
    "Weekend rate — do you charge a surcharge?",
]

BODY_FRAGMENTS = [
    "I'm a new sitter and looking for advice.",
    "Has anyone dealt with this before? Any tips appreciated.",
    "[removed]",
    "Long story short, the booking went weird and I'm not sure what to do.",
    "The puppy was so cute but a handful — any tips on managing energy?",
    "Tried calendar sync with google calendar and it just doesn't work.",
    "Got hit with a 20% fee and I feel like rover's cut is way too much.",
    "Faster payments would solve so many problems — waiting to get paid is rough.",
    "GPS accuracy on rover cards is terrible, tracking is way off.",
    "Considering off platform for repeat clients to avoid the platform fee.",
    "Need a 1099 for taxes and rover support has been slow.",
    "Holiday surcharge season is here — what's your strategy?",
    "Refund came through after 2 weeks, money back finally.",
    "Anyone got a saved response for the meet and greet booking question?",
    "Bookings visibility is so bad — wish there was a better calendar view.",
    "Dropping a client tomorrow because of repeated late pickup — any advice?",
    "Senior dog with medication — special needs pricing?",
    "Looking to grow my business full time on rover, possible?",
    "Glitches on the app made me miss a check in.",
    "Pet insurance liability — covered or not?",
    "",  # empty body, common
    "Cat sitting question — feline experience matters?",
    "Meet and greet — trial booking etiquette?",
    # Edge case: very long body
    "This happened last week and I've been thinking about it ever since. " * 20,
]

AUTHORS = [
    "u/sitter42", "u/dogwalkr", "u/petmom", "u/newsitter", "u/seasoned_sitter",
    "u/walks_and_naps", "u/woofworld", "u/paws_and_pay", "u/the_dog_father",
    "u/catlady99", "u/rovermomof3", "u/petsitterpro", "u/sidehustle_sitter",
    "u/fulltime_walker", "u/anonymous_user", "u/rover_newbie",
]


def synthesize_post(rng: random.Random, base_dt: datetime) -> dict:
    """Return one synthetic post dict shaped like a real parsed sheet row."""
    # Spread ~uniformly over the last 90 days, with small random jitter.
    days_ago = rng.randint(0, 89)
    dt = base_dt - timedelta(days=days_ago, hours=rng.randint(0, 23))

    title = rng.choice(TITLES)
    # ~30% multi-fragment bodies (more keywords → more themes hit)
    if rng.random() < 0.30:
        body = " ".join(rng.sample(BODY_FRAGMENTS, k=rng.randint(2, 3)))
    else:
        body = rng.choice(BODY_FRAGMENTS)

    # Inject occasional very-long titles as an edge case
    if rng.random() < 0.05:
        title = title + " — " + " ".join(rng.sample(BODY_FRAGMENTS[:6], k=2))

    themes, problems = tag_post(title, body)

    # ~10% target untagged: pick a body that's unlikely to fire any keyword.
    if rng.random() < 0.10:
        title = rng.choice([
            "Hey everyone, just joined!",
            "Random thought of the day",
            "Hope you're having a good one",
            "Question about the community",
        ])
        body = rng.choice([
            "Nothing specific to ask, just wanted to say hi.",
            "Felt cute might delete later.",
            "[removed]",
            "",
        ])
        themes, problems = tag_post(title, body)

    # Synthetic but plausible URL — sha1 gives stable id per run via seed.
    url_slug = hashlib.sha1(f"{title}{dt.isoformat()}".encode()).hexdigest()[:8]
    url = f"https://reddit.com/r/RoverPetSitting/comments/{url_slug}/"

    return {
        "id": hashlib.sha1(url.encode()).hexdigest()[:10],
        "date": dt.strftime("%Y-%m-%d"),
        "title": title,
        "url": url,
        "author": rng.choice(AUTHORS),
        "preview": truncate_preview(body),
        "themes": themes,
        "problems": problems,
        "subreddit": "RoverPetSitting",
    }


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--out", required=True, help="Output directory")
    ap.add_argument("--count", type=int, default=200, help="Number of synthetic posts")
    ap.add_argument("--seed", type=int, default=42, help="RNG seed for reproducibility")
    args = ap.parse_args()

    # Sanity check: PROBLEMS came from the same taxonomy we'll write out.
    assert PROBLEMS, "PROBLEMS taxonomy is empty — check rover_sheet_dump import"

    rng = random.Random(args.seed)
    base_dt = datetime.now(timezone.utc)
    posts = sorted(
        (synthesize_post(rng, base_dt) for _ in range(args.count)),
        key=lambda p: p["date"],
    )
    taxonomy = load_taxonomy()
    meta = write_dataset(posts, taxonomy, args.out)
    print(f"Wrote fixture: {meta['post_count']} posts → {args.out}")
    print(f"  posts:      {meta['posts_file']}")
    print(f"  aggregates: {meta['aggregates_file']}")
    print(f"  date range: {meta['date_range']['start']} → {meta['date_range']['end']}")


if __name__ == "__main__":
    main()
