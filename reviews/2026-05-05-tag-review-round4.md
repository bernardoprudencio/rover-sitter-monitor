# Tag Review — Round 4 (2026-05-05)

## Run Summary

| | |
|---|---|
| **Date** | 2026-05-05 (UTC) |
| **Mode** | `posts` — uniform-random sample, same seed as baseline / Round 3 |
| **Reviewer** | Claude Code subagent (general-purpose) |
| **Inputs** | [taxonomy.json](../taxonomy.json) (post-Round-4 edits) + 250 sampled posts |
| **Posts dataset** | `posts.f6a36282.json` — 8,453 posts in tagged pool |
| **Generated at** | 2026-05-05 (post Round-4 retag) |
| **Sample seed** | `20260505` — same seed as baseline / Round 3 |
| **Confidence threshold** | non-correct verdicts emitted at confidence ≥ 0.7 |
| **Sidecar** | [2026-05-05-tag-review-round4.json](2026-05-05-tag-review-round4.json) |

---

## Headline: 84.4% correct — UP from 57.2% Round 3, beats 83.6% baseline

| Verdict | Round 4 | % | Round 3 | % | Δ vs R3 | Baseline | % | Δ vs base |
|---|---|---|---|---|---|---|---|---|
| `correct` | **211** | **84.4%** | 143 | 57.2% | **+27.2 pp** | 209 | 83.6% | **+0.8 pp** |
| `false_positive` | 26 | 10.4% | 50 | 20.0% | -9.6 pp | 11 | 4.4% | +6.0 pp |
| `mixed` | 6 | 2.4% | 18 | 7.2% | -4.8 pp | 5 | 2.0% | +0.4 pp |
| `miscategorized` | 3 | 1.2% | 22 | 8.8% | -7.6 pp | 10 | 4.0% | -2.8 pp |
| `missing_tag` | 4 | 1.6% | 17 | 6.8% | -5.2 pp | 15 | 6.0% | -4.4 pp |
| **total** | **250** | 100% | **250** | 100% | — | **250** | 100% | — |

**95% Wilson CI for correct: 79.4% – 88.4%** — does not overlap Round 3 (51.0%–63.2%); regression from Round 3 fully reversed and recovers to baseline level. Verdict on the goal: **correct ≥ 75% landed; FP rate ≤ 8% missed by 2.4 pp** (10.4% actual). Round 5 should focus on the residual cat/breed/training FP cluster.

The PREVIEW_MAX bump from 200 → 500 chars was the single biggest mechanical fix — every post in this audit had visible fired keywords, eliminating Round 3's "no fired keywords on truncated preview" noise class. The 9 keyword tightenings landed cleanly; no remaining FPs trace to the dropped keywords.

---

## What Round 4 fixed

All nine targeted keyword edits worked. None of the dropped keywords show up as FPs in this sample:

| Round 3 FP keyword | Round 4 action | Round 4 audit shows |
|---|---|---|
| `just started` (Joining and starting on Rover) | Dropped → `just joined rover` added | Zero FPs from the new phrase. The 23 Joining-tagged posts in the sample all fire on legitimate `new to rover` or onboarding language. Only edge case is #244 ("Losing my mind") where `new to rover` matches OP describing the *clients* as new — not addressed by Round 4 edits. |
| `vacation` (Time off / holidays) | Replaced → `my vacation`, `taking vacation`, `going on vacation`, `sitter vacation`, `vacation time` | Zero FPs from `vacation` stems. `going on vacation` fired correctly on owner-prep posts. Two remaining Time off FPs are both from the unchanged `unavailable` stem (#45, #187), not the vacation stems. |
| `old dog` (Senior dogs) | Dropped | Zero FPs. All 4 Senior dogs firings are legitimate `senior dog` / `elderly dog`. |
| `not working` (Glitches / lag / bugs) | Replaced → `app not working` etc. | Zero FPs. Only one Glitches firing (#160, on `bug`), correct. |
| `covered` (Business insurance) | Replaced → `am i covered`, `insurance covered`, `liability covered` | Zero FPs from `covered`. Two remaining Business insurance FPs come from the still-bare `insurance` (#161 health insurance) and `protect` (#242 protect-your-home advice). |
| `advertise` (Self promotion) | Narrowed → `i advertise`, `advertise my`, `advertising my` | Zero FPs. Both Self promotion firings (#53, #65) are legitimate `social media`. |
| bare `reminder` / `remind me` (Reminders) | Replaced → `notification reminder`, `set a reminder`, `app reminder`, `push reminder` | Zero firings of Reminders in the sample at all — passes by lack of evidence. Recall risk is real (see "What got worse"). |
| bare `trial` (Trial) | Replaced → `trial booking`, `trial walk`, `trial sit`, `trial visit`, `trial stay`, `test booking` | Zero firings of Trial in the sample. Recall risk is real (see "What got worse"). |
| `profile page` (Profile customization) | Replaced → `update profile`, `customize profile`, `edit profile`, `profile photo`, `sitter website`, `sitter profile` | One Profile customization firing (#41 `sitter profile` — correct, post is about profile location bug). No FPs. |

The PREVIEW_MAX 200 → 500 change was equally important: the 30 "no fired keywords on truncated preview" findings from Round 3 are gone. Every Round 4 finding has a visible matched keyword, which makes auditing materially less ambiguous.

---

## What's still wrong — recurring FP keyword patterns

26 false positives + 6 mixed = 32 posts where ≥1 tag is wrong. Ranked by frequency within this sample:

| Keyword/phrase | Problem fired | FP cause | Count | Suggested fix |
|---|---|---|---|---|
| `cat` / `cats` (incidental) | Cats and kittens | "the camera caught a cat", "I have a cat", "cats" in a list, **`cat scan` (medical)** | 7 | Bare `cat` is too greedy. Hardest single fix in the taxonomy. Options: drop bare `cat`, keep `cats`, `kitten`, `kittens`, `feline` — accept some recall loss; OR add a negative-context list (e.g., not when `cat scan` is in text) |
| `training` | High quality pet care | "police dog in training", "house-trained", "we have been working on training (the dog)" | 3 | Replace bare `training` with `sitter training`, `pet care training`, `training course`, `training certification`, `dog trainer` (when sitter is the trainer). The `training` keyword conflates dog-training-the-pet with sitter-getting-trained |
| `breed` | Breeds | "small breed owners", "husky/spitz breed", "favorite breed" | 3 | `breed` is fine when paired with restrictions/concerns. Possibly drop bare `breed`, keep `pit bull`, `pitbull`, `aggressive breed`, `restricted breed`, `dangerous breed`, `breed restriction`. Adds modest recall risk |
| `navigate` / `can't find` | Navigation | "navigate the neighborhood (figurative)", "navigate with cats (figurative)", "can't find another spot" | 3 | Replace bare `navigate` → `navigate the app`, `navigate rover`, `navigate menu`, `navigate website`. Replace bare `can't find` → `can't find feature`, `can't find setting`, `can't find page` |
| `unavailable` | Time off / holidays | "sitters were unavailable", "client was unavailable for a call" | 2 | Replace bare `unavailable` → `mark unavailable`, `set unavailable`, `block unavailable`, `i'm unavailable` (sitter perspective) |
| `more clients` | Low demand | "joined Rover to attract more clients" (intent), "I've been getting more clients" (opposite) | 2 | Drop `more clients` from Low demand. Replace with `not enough clients`, `need more clients`, `getting fewer clients`, `slow on clients`. Keep `low demand`, `no bookings`, `slow season` |
| `repeat client` | Flag repeat clients | "this is a repeat client" used as background context | 2 | Hard to fix; semantic. Possibly require co-occurrence with `flag` / `mark` / `manage` / `block` — but that breaks recall on legitimate `repeat client` discussion. Lowest-priority fix |
| `insurance` (bare) | Business insurance | "partner's [health] insurance" | 1 | Replace bare `insurance` → `pet insurance`, `business insurance`, `liability insurance`, `sitter insurance`, `pet care insurance`. Keep already-narrowed `am i covered`, `insurance covered`, `liability covered` |
| `protect` | Business insurance | "Protect your home and fur babies" (advice phrase, not insurance) | 1 | Drop bare `protect`. The keyword is too generic |
| `distance` | Distance | "short distance" of driving (mechanical context) | 1 | Replace bare `distance` → `service distance`, `travel distance`, `walk distance` |
| `same day` | Short lead time | "all happened on the same day" (event clustering, not booking) | 1 | Hard to narrow; keep — single FP across the audit. Same-day context dominates legitimate uses |
| `new to rover` | Joining and starting on Rover | "they're new to Rover" (clients, not sitter) | 1 | Hard to narrow; semantic. Skip |
| `christmas` | Holidays | "Christmas Day House Fire" (date marker, not holiday booking) | 1 | Keep — single FP, recall on Christmas-booking discussions matters |
| `puppy` | Puppies | "the only dog that didn't cry was a puppy" (passing mention) | 1 | Keep — single FP |
| `full-time` / `full time` | Part/full-time | "got a full-time job" (life context, not Rover work) | 1 | Hard to narrow without losing recall on the common "doing Rover full time" usage. Skip |
| `drop off` | Pick-up and drop-off | "drop off time" mentioned in a bite-incident post | 1 | Keep |
| `reimburse` | Refunds | "reimburse the antifreeze" (expense, not refund) | 1 | Keep — overlap with Expenses is a known taxonomy ambiguity, not a keyword fault |
| `neglected` (hygiene) | Lost or injured pet | "neglected hygiene/coat" — dog has bad grooming | 1 | Replace bare `neglected` → `pet neglected`, `dog neglected`, `cat neglected`, `obvious neglect`, `severe neglect` |

**The `cat`/`cats` cluster (7 FPs) is the single largest residual problem.** Round 3's caveat about plural cat stems was real and remains the dominant FP source. This taxonomy is structurally hard to fix without significant recall loss — the word `cat` is too common in pet-sitting posts to land cleanly as a topic indicator. Options to consider in Round 5: drop bare `cat`, keep `cats`/`kitten`/`kittens`/`feline`, AND add explicit phrases like `cat sitter`, `cat sitting`, `cat boarding`, `cat owner`, `kitty`, `kitties` to recover the recall.

---

## What got worse, if anything

Modest recall risks introduced by Round 4 narrowings — none surface as `missing_tag` findings in this audit, but worth tracking:

- **Reminders (0 firings in sample).** With bare `reminder` dropped and the new whitelist (`notification reminder`, `set a reminder`, `app reminder`, `push reminder`, `reminder notification`) being strict noun-phrases, the sample shows zero matches. Either the topic is genuinely rare (likely — Reminders has always been low-volume) or the whitelist is too narrow. Spot-check the broader sheet before next round; if recall has collapsed, add `notification`, `push notif`, `app reminded me`.
- **Trial (0 firings in sample).** Same pattern. The whitelist is restrictive: `trial booking`, `trial walk`, `trial sit`, `trial visit`, `trial stay`, `test booking`. Common phrasings like "trial day", "trial run", "trial period" don't fire. Add these in Round 5 if the topic shows up in untagged posts.
- **Time off / holidays.** Dropping bare `vacation` cleared 3 owner-side FPs from Round 3 — but the still-bare `unavailable` re-introduces 2 of those FPs. The vacation narrowing worked; the unavailable bareness is the new weak spot.

No drops in tagged-pool size flagged. The post-retag tagged-pool size is 8,453 (down from Round 3's 8,677), consistent with FP cleanup intent.

---

## Findings (39 total)

Sorted by severity (`false_positive` > `mixed` > `miscategorized` > `missing_tag`), then confidence DESC. Full list in the [JSON sidecar](2026-05-05-tag-review-round4.json) — top 30 abridged below.

| URL | Verdict | Current → Proposed | Confidence | Rationale |
|---|---|---|---|---|
| [no_more_dogs_who_pull](https://reddit.com/r/RoverPetSitting/comments/1r27ssf/no_more_dogs_who_pull_and_are_on_the_large_side/) | `false_positive` | Cats and kittens → (none) | 0.95 | `cat` matches `cat scan` (medical CT scan); not about cats |
| [harassment_from_neighbor](https://reddit.com/r/RoverPetSitting/comments/1px8k0f/struggling_with_harassment_from_neighbor_on_walks/) | `false_positive` | Navigation → (none) | 0.85 | `navigate` figurative ("navigate the neighborhood safely") |
| [cats](https://reddit.com/r/RoverPetSitting/comments/1nok7zd/cats/) | `false_positive` | Navigation, Cats and kittens → Cats and kittens | 0.85 | `navigate` figurative ("how do you navigate with cats") |
| [vetting_process_last_minute](https://reddit.com/r/RoverPetSitting/comments/1quhiik/seeking_advice_pet_parents_keep_extending_vetting/) | `false_positive` | Time off / holidays, Short lead time, M&G → Short lead time, M&G | 0.85 | `unavailable` = client unavailable for call, not sitter time off |
| [undisclosed_cameras](https://reddit.com/r/RoverPetSitting/comments/1kp8izc/undisclosed_cameras/) | `false_positive` | Business insurance → (none) | 0.85 | `protect` matches "Protect your home and fur babies" — advice, not insurance |
| [longer_term_boarding](https://reddit.com/r/RoverPetSitting/comments/1j3ifhr/longer_term_boarding_question/) | `false_positive` | Navigation, Cats and kittens → Cats and kittens | 0.80 | `can't find` figurative ("can't find another spot to live") |
| [asking_for_refund](https://reddit.com/r/RoverPetSitting/comments/1jjihlh/asking_for_refund/) | `false_positive` | Refunds, Short lead time → Refunds | 0.80 | `same day` = events clustered same day, not booking lead time |
| [sudden_change](https://reddit.com/r/RoverPetSitting/comments/1j08r1k/sudden_change/) | `false_positive` | Cats and kittens → (none) | 0.80 | `cats` only in list "humans, dogs, cats and squirrels" |
| [are_my_new_rates_reasonable](https://reddit.com/r/RoverPetSitting/comments/1mtqcti/are_my_new_rates_reasonable/) | `false_positive` | Low demand → (none) | 0.80 | `more clients` — post is "I've been getting MORE clients", opposite of low demand |
| [new_to_rover_attract_clients](https://reddit.com/r/RoverPetSitting/comments/1n6yues/new_to_rover/) | `false_positive` | Joining, Low demand → Joining | 0.75 | `more clients` — post is intent at signup, not low demand |
| [is_this_frustrating](https://reddit.com/r/RoverPetSitting/comments/1rflydh/is_this_frustrating_or_am_i_overreacting_as_a/) | `false_positive` | Time off, Cats → Cats | 0.75 | `unavailable` = sitters unavailable for booking dates, not vacation |
| [stressing_dog_caused_damage](https://reddit.com/r/RoverPetSitting/comments/1lyijmq/stressingdog_caused_damage_to_my_home_and_i_told/) | `false_positive` | Breeds, M&G → M&G | 0.75 | `breed` in "husky/spitz breed" descriptor |
| [not_house_trained](https://reddit.com/r/RoverPetSitting/comments/1rt3uub/not_house_trained/) | `false_positive` | High quality pet care → (none) | 0.75 | `training` = house-training a dog, not sitter education |
| [losing_my_mind](https://reddit.com/r/RoverPetSitting/comments/1mijiqk/losing_my_mind/) | `false_positive` | Joining → (none) | 0.75 | `new to rover` refers to the CLIENTS, not the sitter |
| [car_issues](https://reddit.com/r/RoverPetSitting/comments/1lvxrt8/car_issues/) | `false_positive` | Distance → (none) | 0.75 | `distance` = "short distance" of driving (mechanical context) |
| [showing_appreciation](https://reddit.com/r/RoverPetSitting/comments/1iwll4v/showing_appreciation/) | `false_positive` | Breeds → (none) | 0.70 | `breed`, `pitbull` incidental — post is gift-giving |
| [why_dont_clients_train](https://reddit.com/r/RoverPetSitting/comments/1nx2dk0/why_dont_clients_train_their_dogs_anymore_rant/) | `false_positive` | Breeds → (none) | 0.70 | `breed` in "small breed owners" — incidental modifier |
| [crate_dogs](https://reddit.com/r/RoverPetSitting/comments/1nyc0ux/dogs_that_stay_at_my_apartment_hate_the_crate/) | `false_positive` | Puppies → (none) | 0.70 | `puppy` mentioned in passing — post is about adult dogs |
| [christmas_house_fire](https://reddit.com/r/RoverPetSitting/comments/1r2iv5v/christmas_day_house_fire_during_rover_booking/) | `false_positive` | Holidays → (none) | 0.70 | `christmas` is a date marker; topic is house fire damages |
| [bad_sitters_frustrate_me](https://reddit.com/r/RoverPetSitting/comments/1j3qah8/bad_sitters_frustrate_me/) | `false_positive` | Cats, M&G → M&G | 0.70 | `cat` is one detail in a bad-sitter rant |
| [new_to_rover_bristol](https://reddit.com/r/RoverPetSitting/comments/1ohaln8/new_to_rover_as_dog_sitter_in_bristol_no_bookings/) | `false_positive` | Joining, Low demand, Cats → Joining, Low demand | 0.70 | `cat` only in profile photo description |
| [he_says_it_was_a_mistake](https://reddit.com/r/RoverPetSitting/comments/1m631yn/he_says_it_was_a_mistake_but/) | `false_positive` | Cats and kittens → (none) | 0.70 | `cat` incidental; topic is creepy client message |
| [accused_of_stealing_a_cup](https://reddit.com/r/RoverPetSitting/comments/1p9ging/accused_of_stealing_a_cup/) | `false_positive` | Part/full-time → (none) | 0.70 | `full-time` as life context ("got a full-time job"), not Rover work |
| [boarding_guidelines](https://reddit.com/r/RoverPetSitting/comments/1r1xa2t/boarding_guidelines/) | `false_positive` | Cats → (none) | 0.70 | `cats` incidental ("I have cats"); post is about boarding policies |
| [working_dog](https://reddit.com/r/RoverPetSitting/comments/1n1hf8m/has_anybody_cared_for_a_working_dog/) | `false_positive` | High quality pet care → (none) | 0.70 | `training` = "police dog in training" — dog being trained, not sitter |
| [losing_his_hearing](https://reddit.com/r/RoverPetSitting/comments/1j3fky4/think_a_dog_under_my_care_is_losing_his_hearing/) | `false_positive` | Flag repeat clients → (none) | 0.70 | `repeat client` is descriptive context; topic is hearing loss |
| [dog_had_an_incident](https://reddit.com/r/RoverPetSitting/comments/1m8vnpj/dog_had_an_incident_at_home_owner_seems_to_be/) | `mixed` | Pick-up/drop-off → Cancellations, Safety and aggression | 0.85 | `drop off` incidental; topic is dog biting child + cancellation |
| [cancer_diagnosis](https://reddit.com/r/RoverPetSitting/comments/1kjjmri/should_i_disclose_my_recent_cancer_diagnosis_if/) | `mixed` | Star ratings, Business insurance, Part/full-time → Star ratings, Part/full-time | 0.85 | `insurance` = partner's HEALTH insurance, not business insurance |
| [stats_glitch](https://reddit.com/r/RoverPetSitting/comments/1m9vh8s/anyone_else_having_issues_with_the_app_not/) | `mixed` | Insights, Flag repeat clients → Insights, Glitches / lag / bugs | 0.75 | `repeat client` FP; missing Glitches |
| [bunnies](https://reddit.com/r/RoverPetSitting/comments/1rqg3ba/bunnies/) | `mixed` | Cats, Other pets → Other pets | 0.75 | `cat` = rabbit registered as cat in app — incidental |

(Full 39 in the JSON sidecar, ordered identically.)

---

## Round 5 plan

Round 4 hit the `correct ≥ 75%` target with margin (84.4%). The FP rate of 10.4% is just above the 8% goal — closing that gap is Round 5's main job. Recall (`missing_tag` rate of 1.6%) is in great shape; do not expand keywords speculatively.

### Recommended apply order (Round 5)

1. **Tackle the `cat` / `cats` FP cluster** — 7 of 26 FPs (27%). This is the single biggest lever. Best option (in priority order):
   - **(a) Drop bare `cat`.** Keep `cats`, `kitten`, `kittens`, `feline`. Add `cat sitter`, `cat sitting`, `cat boarding`, `cat owner`, `cat client`, `kitty`, `kitties`, `cat drop`, `cat litter`, `cat parent`. This kills FPs like `cat scan`, "I have a cat", "registered as a cat" while preserving recall on actual cat-sitting posts (most of which mention `cats` plural anyway).
   - **(b)** Alternative: keep bare `cat` but blocklist co-occurrences with `cat scan`, `cat litter` (paradoxical — keep that), `bobcat`, `wildcat`. Brittle and not recommended.
   - Test on this audit's 7 FPs after applying.

2. **Narrow `training` in High quality pet care** — 3 FPs. Replace bare `training` with: `sitter training`, `pet care training`, `training certification`, `training course`, `dog trainer` (sitter-as-trainer), `behavior training` (when sitter-discussed). Keep `certification`, `courses`, `high quality`, `better care`, `improve care`.
   - Side effect: posts where sitter offers Training as a service (#108, #221, #167, #206) still fire on the new variants. Posts about *the dog being trained* (#218, #219, #156) drop out — desired.

3. **Narrow `breed` in Breeds** — 3 FPs. Replace bare `breed` with: `breed restriction`, `dog breed`, `breed list`, `breed concern`, `specific breed`, `which breeds`. Keep `pit bull`, `pitbull`, `aggressive breed`, `restricted breed`, `dangerous breed`. Add `bully breed`, `breed ban`, `breed restricted`. The "favorite breed" / "small breed owners" / "husky/spitz breed" descriptive uses drop out.

4. **Narrow `unavailable`** — 2 FPs. Replace bare `unavailable` with: `mark unavailable`, `set unavailable`, `block unavailable`, `i'm unavailable`, `not available those dates`. Keep `time off`, `going on vacation`, `taking vacation`, `my vacation`, `vacation time`, `block off`, `sitter vacation`.

5. **Narrow `more clients` and `navigate`/`can't find`** — 2 FPs each.
   - `more clients` (Low demand): drop. Replace with `not enough clients`, `need more clients`, `getting fewer clients`. Keep `low demand`, `no bookings`, `slow season`.
   - `navigate`/`can't find` (Navigation): replace with `navigate the app`, `navigate rover`, `navigate menu`, `navigate website`, `can't find feature`, `can't find setting`, `can't find page`, `can't find option`, `where is the`, `hard to find feature`. Keep general `navigation`, `hard to find`.

6. **Narrow `insurance`, `protect`, `neglected`, `distance`** — 1 FP each.
   - `insurance` (Business insurance): replace bare `insurance` with `pet insurance`, `business insurance`, `liability insurance`, `sitter insurance`, `pet care insurance`, `insurance for`. Keep already-narrowed `am i covered`, `insurance covered`, `liability covered`.
   - `protect` (Business insurance): drop. Too generic to keep.
   - `neglected` (Lost or injured pet): replace bare `neglected` / `neglects` with `pet neglected`, `dog neglected`, `cat neglected`, `obvious neglect`, `severe neglect`, `neglectful sitter`. Keep `neglect` general, `lost the dog`, `dog escaped`, etc.
   - `distance` (Distance): replace bare `distance` with `service distance`, `travel distance`, `walk distance`, `driving distance`, `commute distance`. Keep `how far`, `service area`.

7. **Then do not touch: `same day`, `christmas`, `puppy`, `full-time`, `drop off`, `repeat client`, `reimburse`, `new to rover`** — each contributes 1 FP and the keyword has clear legitimate use that would drop with narrowing. Accept the residual.

8. **Spot-check Reminders and Trial recall.** Both produced zero firings in this 250-post sample after Round 4 narrowing. Either the topic is rare (likely) or the whitelist is too strict. Sample 50 untagged posts from the post-Round-5 export and look for `reminder`/`trial`-stem matches that should fire. If recall has collapsed, add `notification` / `app reminded me` (Reminders) and `trial day`, `trial period`, `trial run` (Trial).

9. **Re-audit.** Target Round 5: `correct ≥ 88%`, FP rate ≤ 6%.

### Resume context (read this first on a fresh session)

- **Working tree:** Round 4 taxonomy edits are **uncommitted** in [taxonomy.json](../taxonomy.json) and [rover_export_json.py](../rover_export_json.py) (PREVIEW_MAX bump). `git diff` shows them. The most recent commit `c8fb4a0` covers Rounds 1+2+3 only. Branch is `claude/trusting-payne-3ab4da`. Sample input lives at [reviews/round4_input/sample_250.json](round4_input/sample_250.json) — do not modify it.
- **Sheet state:** retagged on 2026-05-05 (post-Round-4 retag); tagged-pool size **8,453 posts** (down from Round 3's 8,677 — net 224 posts dropped via narrowing, consistent with the 9 FP-cleanup edits).
- **Operational nuance:** running `python3 rover_sheet_dump.py --retag` or `make export` requires:
  1. `credentials.json` in cwd (this worktree's symlink points to the main repo's file; gitignored)
  2. `SHEET_ID` env var — source it with: `set -a && . /Users/bernardoprudencio/Documents/rover-repo/rover-sitter-monitor/.env && set +a`
- **Resolved in Round 4:** dashboard preview is now 500 chars ([rover_export_json.py:24](../rover_export_json.py:24)), matching what `tag_post` sees. The Round 3 "no fired keywords on truncated preview" finding class is gone — every Round 4 finding has a visible fired keyword.
- **Outstanding question** (still open): `trust and safety` is deliberately in BOTH `Safety and aggression incidents` and `Rover Support quality` (creates a dual-fire). User aware; not flagged in Round 4 as a problem.

### Files to read on resume

- [reviews/2026-05-05-tag-review-round4.md](2026-05-05-tag-review-round4.md) — this file (Round 4 results + Round 5 plan)
- [reviews/2026-05-05-tag-review-round4.json](2026-05-05-tag-review-round4.json) — 39 findings as structured JSON
- [reviews/2026-05-05-tag-review-round3.md](2026-05-05-tag-review-round3.md) — Round 3 results (the regression Round 4 fixed)
- [reviews/2026-05-05-tag-review-baseline.md](2026-05-05-tag-review-baseline.md) — original 83.6% baseline; Round 3 changelog at the bottom
- [taxonomy.json](../taxonomy.json) — current taxonomy (Rounds 1+2+3+4 edits, committed)
- [rover_sheet_dump.py](../rover_sheet_dump.py) — `tag_post` matcher (line 48); `--retag` mode (line 263)
- [rover_export_json.py](../rover_export_json.py) — `PREVIEW_MAX = 500` lives here (line 24); raised in Round 4

### Re-run command

```bash
set -a && . /Users/bernardoprudencio/Documents/rover-repo/rover-sitter-monitor/.env && set +a
python3 rover_sheet_dump.py --retag      # propagate Round 5 taxonomy to sheet
make export                               # refresh dashboard data (new posts.<hash>.json filename)
# then sample 250 posts uniformly from the new tagged pool with seed 20260505,
# spawn a general-purpose subagent with the same audit protocol used in this round.
```

---

*Generated by uniform-random tag audit on 2026-05-05 post-Round-4 retag. Sample is unbiased over the new tagged pool of 8,453 posts. The 84.4% headline reflects accuracy after Round 4's 9-keyword FP cleanup. Round 5 should focus on the `cat`/`training`/`breed` residual cluster (13 of 26 FPs) — closing those would push the correct rate well above 90%.*
