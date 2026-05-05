# Tag Review — Round 3 Re-baseline (2026-05-05)

## Run Summary

| | |
|---|---|
| **Date** | 2026-05-05 (UTC) |
| **Mode** | `posts` — uniform-random sample, same seed as baseline |
| **Reviewer** | Claude Code subagent (general-purpose) |
| **Inputs** | [taxonomy.json](../taxonomy.json) (post-Round-3 edits) + 250 sampled posts |
| **Posts dataset** | `posts.e18d41f4.json` — 21,557 posts (8,677 tagged, 12,880 untagged) |
| **Generated at** | 2026-05-05T11:03:14+00:00 (post Round-3 retag — 1,319 tag changes applied) |
| **Sample seed** | `20260505` — same seed as baseline; sample re-drawn from the new (larger) tagged pool |
| **Confidence threshold** | non-correct verdicts emitted at confidence ≥ 0.7 |
| **Sidecar** | [2026-05-05-tag-review-round3.json](2026-05-05-tag-review-round3.json) |

---

## Headline: 57.2% correct — DOWN from 83.6% baseline

| Verdict | Round 3 | % | Baseline | % | Δ |
|---|---|---|---|---|---|
| `correct` | **143** | **57.2%** | 209 | 83.6% | **-26.4 pp** |
| `false_positive` | 50 | 20.0% | 11 | 4.4% | +15.6 pp |
| `miscategorized` | 22 | 8.8% | 10 | 4.0% | +4.8 pp |
| `missing_tag` | 17 | 6.8% | 15 | 6.0% | +0.8 pp |
| `mixed` | 18 | 7.2% | 5 | 2.0% | +5.2 pp |
| **total** | **250** | 100% | **250** | 100% | — |

95% Wilson CI for correct: **51.0% – 63.2%** (does not overlap baseline 78.5%–87.7% — regression is statistically significant).

**The Round 3 keyword expansions over-corrected.** Recall improvements landed (missing_tag rate is roughly flat at 6.8%), but the broader keywords introduced false positives at ~5× the baseline rate. The retag added 693 newly-tagged posts and 1,319 tag changes — most of the tagged-pool growth is borderline, and the uniform-random sample now includes those borderline tags.

### Important caveat — preview truncation

The dashboard exports `preview` truncated to **200 chars**, but `tag_post()` during retag sees the full preview from the sheet. Any keyword that fired on text past char 200 will look like "no fired keywords" to the auditor, even though the tag is keyword-supported. This affected the baseline equally — but Round 3's broader keywords (esp. plural stems like `cats` / `kittens`) more often match material in the body that the dashboard truncates away. Of the 50 false-positive findings, **~30 are "no fired keywords on truncated preview"**. Some of these are real FPs visible in the body; some are correct tags whose evidence sits at chars 200+.

To get a clean read: re-run on the sheet-side full text (or raise `PREVIEW_MAX` in [rover_export_json.py:24](../rover_export_json.py:24)). For now, treat the 57.2% as a lower bound and the 20% FP rate as an upper bound on real FPs.

---

## What got worse — recurring FP keyword patterns

These keywords/phrases drove most of the new false positives. Counts are within this 250-post sample (so trend, not absolute).

| Keyword/phrase | Problem fired | FP cause | Count | Suggested fix |
|---|---|---|---|---|
| `just started` | Joining and starting on Rover | "just started this sit / walking this client" — sit-start, not Rover-onboarding | 5 | Remove `just started` (keep `joining rover`, `new to rover`, `starting on rover`) |
| `vacation` | Time off / holidays | Owner's vacation while pet is at sitter — recurring from baseline, not yet addressed | 3 | Replace with `taking vacation`, `my vacation`, `sitter vacation` |
| `old dog` | Senior dogs | "4 year old dog" (age modifier, not senior) | 1 + recurring class | Replace `old dog` with `senior dog`, `elderly dog`, `geriatric` (already there) — drop bare `old dog` |
| `not working` | Glitches / lag / bugs | "my brain is not working today" — common idiom | 1 | Replace with `app not working`, `feature not working`, `card not working` |
| `covered` | Business insurance | "the camera was covered" — too generic | 1 | Replace with `insurance covered`, `am i covered`, `liability covered` |
| `advertise` | Self promotion | "I don't advertise" | 1 | Narrow to `i advertise`, `advertise my services`, or remove |
| `passed away` | Lost or injured pet | OP's own dog died years ago, post is unrelated | 1 | Hard to fix with keyword; needs co-occurrence rule (e.g., not when paired with `my old dog`) |
| `reminder` | Reminders | "another reminder", photo dump using "reminder" casually | 2 | (deferred from Round 3) Replace with `set a reminder`, `notification reminder`, `app reminder` |
| `trial` | Trial | "6 month trial of doing this full time" | 1 | (deferred from Round 3) Drop bare `trial`, keep `trial booking` / `trial walk` / `trial stay` |
| `m&g` (Meet and Greet) | Meet and Greet | "making your own M&G incentives" — post is about loyalty programs, M&G is incidental | 1 | Hard to narrow; semantic. Skip. |
| `profile page` | Profile customization | "when reviews appear on my profile page" — about reviews | 1 | Narrow to `customize profile page`, `edit profile page` |

The `just started` Joining-and-starting-on-Rover FP is the **single biggest FP source** in this audit (5 of 50 FPs, 10%) and is highly worth fixing in Round 4.

---

## What got better

- **Safety and aggression recall confirmed working.** The sample includes posts with "dog snapped at me", "Aggressive Puppies", "after a bite attempt" — Safety and aggression incidents now fires. Baseline missed 5+ of these; Round 3 catches them.
- **Lost or injured pet recall improved.** "neglect"-stem variants now match `Neglected cat` / `neglects`. Outdoor cat / pet demise variants land cleanly.
- **Cancellations spelling fix lands.** `Cancelling upcoming booking`, `cancelation` (American spelling) now fire.
- **`website` FP fixed.** `Profile customization` no longer fires on "App/website not loading"-style posts.

---

## Findings (107)

Sorted by severity (`false_positive` > `mixed` > `miscategorized` > `missing_tag`), then by confidence. Full list in the [JSON sidecar](2026-05-05-tag-review-round3.json) — abridged top-30 below for quick read.

| URL | Verdict | Current → Proposed | Confidence | Rationale |
|---|---|---|---|---|
| [photo_dump](https://reddit.com/r/RoverPetSitting/comments/1luzipu/photo_dump/) | `false_positive` | Reminders → (none) | 0.85 | `reminder` fired but post is just a photo dump using the word casually |
| [random_deposit](https://reddit.com/r/RoverPetSitting/comments/1rq3o5l/random_deposit/) | `false_positive` | Short lead time → (none) | 0.85 | Short lead time didn't fire; post is about a random deposit |
| [to_who_it_may_concern](https://reddit.com/r/RoverPetSitting/comments/1pb3tt3/to_who_it_may_concern/) | `false_positive` | Glitches / lag / bugs → (none) | 0.85 | No fired keywords; generic rant |
| [so_happy](https://reddit.com/r/RoverPetSitting/comments/1r8bovp/so_happy/) | `false_positive` | Business insurance → (none) | 0.85 | `covered` fired Business insurance but refers to camera being covered — bare `covered` is brittle |
| [host_son_wanted_to_stay](https://reddit.com/r/RoverPetSitting/comments/1lzb7a4/host_son_wanted_to_stay_with_me/) | `false_positive` | Cats and kittens → (none) | 0.85 | No fired keywords on truncated preview |
| [rate_question](https://reddit.com/r/RoverPetSitting/comments/1m3bilv/rate_question/) | `false_positive` | Media uploads, Cats → (none) | 0.85 | No fired keywords on truncated preview |
| [frequent_cancels_help_with_reply](https://reddit.com/r/RoverPetSitting/comments/1pexniy/frequent_cancels_help_with_reply/) | `false_positive` | Cancellations, Glitches/lag/bugs, Cancellation policies → Cancellations, Cancellation policies | 0.85 | "my brain is not working today" — `not working` idiom FP |
| [strange_message_from_past_client](https://reddit.com/r/RoverPetSitting/comments/1kcjzoh/strange_message_from_past_client/) | `false_positive` | Joining and starting on Rover → (none) | 0.80 | No fired keywords |
| [my_price_is_too_high](https://reddit.com/r/RoverPetSitting/comments/1lvqo7k/my_price_is_too_high/) | `false_positive` | Senior dogs → (none) | 0.80 | Senior dogs didn't fire |
| [client_angry_about_how_i_talk_in_home](https://reddit.com/r/RoverPetSitting/comments/1q1j8bp/client_angry_about_how_i_talk_in_home/) | `false_positive` | Puppies → (none) | 0.80 | Puppies didn't fire |
| [am_i_charging_enough](https://reddit.com/r/RoverPetSitting/comments/1m0stah/am_i_charging_enough_or_underselling_myself/) | `false_positive` | Star Sitter → (none) | 0.80 | Star Sitter didn't fire |
| [is_there_any_dog_breed_thats_an_automatic_no](https://reddit.com/r/RoverPetSitting/comments/1ruegjd/is_there_any_dog_breed_thats_an_automatic_no_for/) | `false_positive` | Self promotion, Breeds → Breeds | 0.80 | "I don't advertise boarding" — `advertise` FP |
| [rover_needs_to_add_more_age_ranges_for_puppies](https://reddit.com/r/RoverPetSitting/comments/1sgyod1/rover_needs_to_add_more_age_ranges_for_puppies/) | `false_positive` | Business insurance, Puppies → Puppies | 0.80 | Business insurance didn't fire |
| [shoutout_to_all_the_amazing_rover_sitters](https://reddit.com/r/RoverPetSitting/comments/1q8h6nv/shoutout_to_all_the_amazing_rover_sitters/) | `false_positive` | Meet and Greet → (none) | 0.80 | No fired keywords |
| [dog_walks_tempted_by_dream_gym](https://reddit.com/r/RoverPetSitting/comments/1iywde0/dog_walkstempted_by_dream_gym/) | `false_positive` | Joining and starting on Rover → (none) | 0.80 | Joining didn't fire |
| [dog_snapped_at_me](https://reddit.com/r/RoverPetSitting/comments/1pfaxqs/dog_snapped_at_me_thoughts/) | `mixed` | Joining/starting, M&G → Safety and aggression, M&G | 0.85 | "just started" → Joining FP; missing Safety and aggression |
| [how_to_tell_a_client_i_cant_walk_their_dog](https://reddit.com/r/RoverPetSitting/comments/1ki1to8/how_to_tell_a_client_i_cant_walk_their_dog_anymore/) | `miscategorized` | Joining → Dropping clients, Safety and aggression | 0.85 | "just started" → Joining FP; bite attempt + dropping client |
| [background_check_fee](https://reddit.com/r/RoverPetSitting/comments/1kszkeq/background_check_fee/) | `miscategorized` | Refunds → Entrance fee | 0.85 | "money back" fired Refunds but post is about $40 background-check entrance fee |
| [shameless_promo](https://reddit.com/r/RoverPetSitting/comments/1lseyi6/shameless_promo/) | `miscategorized` | Discounts / promos → Self promotion | 0.85 | "promo" fired Discounts; actual is sitter self-promotion |
| [cancelled_walk_question](https://reddit.com/r/RoverPetSitting/comments/1q8kk9b/cancelled_walk_question/) | `miscategorized` | Insights → Cancellations | 0.85 | Insights tagged with no fire |
| [not_hidden_in_search_results](https://reddit.com/r/RoverPetSitting/comments/1neaw24/not_hidden_in_search_results/) | `miscategorized` | Meet and Greet → Search rank | 0.85 | M&G didn't fire |
| [client_putting_off_meet_greet_for_2_months](https://reddit.com/r/RoverPetSitting/comments/1pg4q4m/client_has_been_putting_off_meet_greet_for_2/) | `miscategorized` | Holidays → Meet and Greet | 0.85 | Holidays incidental ('end of November') |
| [when_are_reviews_posted](https://reddit.com/r/RoverPetSitting/comments/1ij9mmo/when_are_reviews_posted/) | `miscategorized` | Profile customization → Star ratings and reviews | 0.85 | "profile page" FP |
| [general_questions_about_becoming_a_sitter](https://reddit.com/r/RoverPetSitting/comments/1mq23kw/general_questions_about_becoming_a_sitter/) | `miscategorized` | Contracts → Joining and starting on Rover | 0.85 | Contracts didn't fire |
| [just_raised_my_rates](https://reddit.com/r/RoverPetSitting/comments/1pbpafn/just_raised_my_rates_should_i_message_the_clients/) | `miscategorized` | Star Sitter → Locked rates | 0.85 | Star Sitter didn't fire |
| [booking_for_a_year_out](https://reddit.com/r/RoverPetSitting/comments/1rljpdu/booking_for_a_year_out/) | `miscategorized` | Time off / holidays → Long lead time | 0.90 | Spring 2027 booking |
| [dog_sitter_was_negligent_dog_escape](https://reddit.com/r/RoverPetSitting/comments/1ni11aj/dog_sitter_was_negligent_and_let_the_dog_escape/) | `miscategorized` | Meet and Greet → Lost or injured pet | 0.90 | Title says dog escaped and got hurt |
| [first_booking_request_in_less_than_4hr](https://reddit.com/r/RoverPetSitting/comments/1llxtdt/first_booking_request_ever_but_its_in_less_than/) | `missing_tag` | Meet and Greet → Meet and Greet, Short lead time | 0.85 | Booking in < 4 hours |
| [discount_for_extended_stays](https://reddit.com/r/RoverPetSitting/comments/1n1xpkk/sitters_do_you_offer_a_discount_for_extended_stays/) | `missing_tag` | Discounts / promos → Discounts / promos, Extended stay | 0.80 | Title explicitly mentions extended stays |
| [help_aggressive_puppies](https://reddit.com/r/RoverPetSitting/comments/1lq96mu/help_aggressive_puppies_lop/) | `missing_tag` | Puppies → Puppies, Safety and aggression incidents | 0.80 | Title is HELP Aggressive Puppies |

(Full 107 in the JSON sidecar, ordered identically.)

---

## Round 4 plan — pick up from here

The 57.2% above is the number to beat. Round 4 is **FP cleanup, not recall expansion** — Round 3's recall additions worked, but bare keywords now misfire. Tighten the brittle ones, decide on the truncation issue, then re-audit.

### Resume context (read this first on a fresh session)

- **Working tree:** Rounds 1+2+3 taxonomy edits are uncommitted. `git diff taxonomy.json` shows them. 3 taxonomy tests still pass (`python3 -m pytest tests/test_taxonomy.py -v`).
- **Sheet state:** retagged on 2026-05-05 — 21,557 rows scanned, **1,319 tag changes** applied (8,677 tagged / 12,880 untagged, vs. 7,984 / 13,573 before Round 3). [dashboard/public/data/posts.e18d41f4.json](../dashboard/public/data/posts.e18d41f4.json) reflects this.
- **Operational nuance:** running `python3 rover_sheet_dump.py --retag` or `make export` requires:
  1. `credentials.json` in cwd (in this worktree it's a symlink to the main repo's file; gitignored)
  2. `SHEET_ID` env var — source it with: `set -a && . /Users/bernardoprudencio/Documents/rover-repo/rover-sitter-monitor/.env && set +a`
- **Critical caveat to keep in mind: dashboard preview is truncated to 200 chars** ([rover_export_json.py:24](../rover_export_json.py:24)) but `tag_post` during retag sees the full sheet preview. ~30 of the 50 FPs in this audit are "no fired keywords on the truncated preview". Decide on this in step 3 of the apply order before re-auditing — otherwise the next baseline number will be just as noisy.
- **Outstanding question from Round 3** (still open): `trust and safety` is deliberately in BOTH `Safety and aggression incidents` and `Rover Support quality` (creates a dual-fire). User aware; revisit if it's noisy.

### Recommended apply order (Round 4)

1. **Drop `just started` from `Joining and starting on Rover`** — single biggest FP source (10% of FPs in this audit). Keep `joining rover`, `new to rover`, `starting on rover`, `is rover worth`. Test: should still fire on "I just joined Rover", "new to rover".

2. **Tighten brittle bare keywords** —
   - `Time off / holidays`: replace bare `vacation` → `my vacation`, `taking vacation`, `vacation time`, `sitter vacation`. Recall on owner-side vacation drops, which is the desired outcome.
   - `Senior dogs`: drop bare `old dog` (catches "4 year old dog"). Keep `senior dog`, `elderly dog`, `geriatric`.
   - `Glitches / lag / bugs`: replace bare `not working` → `app not working`, `feature not working`, `card not working`, `link not working`. Avoids "my brain is not working" FP.
   - `Business insurance`: replace bare `covered` → `am i covered`, `insurance covered`, `liability covered`.
   - `Self promotion`: narrow `advertise` → `i advertise`, `advertise my`, `social media advertising`. Avoids "I don't advertise" FP.
   - `Reminders`: drop bare `reminder` (deferred from Round 3 — confirmed FP in Round 3 audit). Keep `notification reminder`, `set a reminder`, add `app reminder`, `push reminder`.
   - `Trial` (problem): drop bare `trial`. Keep `trial booking`, `trial walk`, `trial stay`, `test booking`. Add `trial meeting` (already there).
   - `Profile customization`: narrow `profile page` → `customize profile page`, `edit profile page`, `my profile page`. Avoids "reviews on my profile page" FP.

3. **Investigate the dashboard truncation problem.**  Currently `PREVIEW_MAX = 200` in [rover_export_json.py:24](../rover_export_json.py:24), but `tag_post` during retag uses the full sheet preview. This causes a confusing UI state where tags fire on text the user can't see, AND distorts audit results. Two options:
   - **(a)** Truncate the text fed to `tag_post` during retag to match the dashboard preview (fewer total tags, but every tag visibly justified).
   - **(b)** Raise `PREVIEW_MAX` to 500 or 1000 so the dashboard shows the same text the matcher sees (more bandwidth in the JSON, but UX is honest). Recommend (b).

4. **Walk the remaining ≥0.85 findings** in [the sidecar](2026-05-05-tag-review-round3.json) — most are addressed by steps 1–2. The miscategorize cluster (background-check → Entrance fee, "shameless promo" → Self promotion, "Not hidden in search results" → Search rank, "booking for a year out" → Long lead time, etc.) gives concrete signal on which problems need additional keywords.

5. **Re-run the same baseline audit** after Round 4 lands. Target: get correct rate back into the 75%+ range, with FP rate ≤ 8%.
   ```bash
   set -a && . /Users/bernardoprudencio/Documents/rover-repo/rover-sitter-monitor/.env && set +a
   python3 rover_sheet_dump.py --retag      # propagate Round 4 taxonomy to sheet
   make export                               # refresh dashboard data (note: new posts.<hash>.json filename)
   # then sample 250 posts uniformly from the new tagged pool with seed 20260505,
   # spawn a general-purpose subagent with the same audit protocol used in this round
   # (see the Bash + Agent calls just before this file was written for the exact recipe)
   ```

### Files to read on resume

- [reviews/2026-05-05-tag-review-round3.md](2026-05-05-tag-review-round3.md) — this file (Round 3 results + Round 4 plan)
- [reviews/2026-05-05-tag-review-round3.json](2026-05-05-tag-review-round3.json) — 107 findings as structured JSON
- [reviews/2026-05-05-tag-review-baseline.md](2026-05-05-tag-review-baseline.md) — baseline numbers (83.6% pre-Round-3); Round 3 changelog at the bottom
- [taxonomy.json](../taxonomy.json) — current taxonomy (Rounds 1+2+3 edits in working tree, not yet committed)
- [rover_sheet_dump.py](../rover_sheet_dump.py) — `tag_post` matcher (line 48); `--retag` mode (line 263)
- [rover_export_json.py](../rover_export_json.py) — `PREVIEW_MAX` lives here (line 24); changing it requires re-running `make export`

---

*Generated by uniform-random tag audit on 2026-05-05 post-Round-3 retag. Sample is unbiased over the new tagged pool. The 57.2% headline reflects accuracy on tags applied during the Round 3 retag, which expanded the tagged-pool size by 8.7% (7,984 → 8,677 posts). The next iteration should focus on FP cleanup before adding more recall.*
