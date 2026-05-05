# Tag Review — 2026-05-05

## Run Summary

| | |
|---|---|
| **Date** | 2026-05-05 (UTC) |
| **Mode** | `taxonomy` (structure-only audit) |
| **Reviewer** | Claude Code subagent (general-purpose) |
| **Inputs** | [taxonomy.json](../taxonomy.json) — 13 themes, 102 problems |
| **Posts dataset** | not loaded (taxonomy-only mode) |
| **Findings** | 10 overlaps · 41 brittle keywords · 15 gaps = **66 actionable suggestions** |
| **Sidecar** | [reviews/2026-05-05-tag-review.json](2026-05-05-tag-review.json) |

> Posts audit and untagged audit were skipped — they need an exported dataset (`make export`). Re-run `/audit-tags posts` and `/audit-tags untagged` after exporting.

---

## 1. Overlaps

Pairs of problems where keywords or scope collide, causing dual firing or ambiguous tagging.

### High-confidence (≥ 0.85)

#### `Going off app` ↔ `Off-platform management`  · confidence 0.90
Both share the exact keywords `off platform` / `off-platform`. A post about managing existing clients off-platform tags both — even though Diversion is about *leaving* Rover entirely while Off-platform management is workflow tooling within an existing client relationship.

```json
{"action": "narrow", "target": "Off-platform management",
 "remove": ["off platform", "off-platform"],
 "add": ["manage outside app", "track outside rover", "spreadsheet for clients"]}
```

#### `Cancellations` (Business) ↔ `Cancellation policies` (Recurring billings) · confidence 0.90
Business `Cancellations` uses `cancellation policy` as a keyword — the literal name of the Recurring-billings problem. Any post mentioning cancellation policy fires both.

```json
{"action": "narrow", "target": "Cancellations",
 "remove": ["cancellation policy"]}
```

#### `Long lead time` ↔ `Short lead time` · confidence 0.85
`Long lead time` uses the broad `lead time` keyword which fires on short-lead-time complaints too.

```json
{"action": "narrow", "target": "Long lead time",
 "remove": ["lead time"],
 "add": ["long lead time", "too far in advance", "far in advance"]}
```

#### `Star Sitter` ↔ `Star ratings and reviews` · confidence 0.85 (via brittle `stars`)
`Star ratings and reviews` uses bare `stars` which is generic and pet-content-adjacent.

```json
{"action": "narrow", "target": "Star ratings and reviews",
 "remove": ["stars"], "add": ["5 stars"]}
```

### Medium confidence (0.65 – 0.84)

| Problems | Confidence | Recommendation |
|---|---|---|
| `Glitches / lag / bugs` ↔ `Glitches and bugs (Cards)` | 0.80 | Add `app` qualifier to general bucket; let card-specific keywords stand alone for card posts |
| `Recurring bookings` ↔ `Customize schedule` (whole Recurring billings theme) | 0.70 | Rename `Recurring bookings` → `Recurring rates` with rate-only keywords, or merge into Recurring billings theme |
| `Pricing transparency` ↔ `Paying upfront` (on `upfront`) | 0.65 | Re-scope: Pricing transparency = visibility of cost; Paying upfront = payment timing |
| `Reminders` ↔ `Functionality` | 0.65 | Split `Functionality` into named features (Message reactions, Search inbox, Timezone display) |

### Lower confidence (0.60 – 0.64)

- `Centralize on clients` ↔ `Off-platform management` — sharpen: native CRM vs. external-tool support
- `Capacity comprehension` ↔ `Dog sizes` — sharpen: numeric count vs. size-tier preferences

---

## 2. Brittle keywords

Keywords likely to misfire on common English usage. The matcher is whole-word case-insensitive — these will fire on huge swathes of unrelated content.

### Critical (≥ 0.90 confidence) — fix first

| Problem | Keyword | Why it misfires | Fix |
|---|---|---|---|
| `Tipping` | `tip` | "a tip for new sitters", "tip: bring a leash" — every tips-and-tricks post | replace → `left a tip` |
| `Working hours` | `bother me` | "the dog doesn't bother me" — extremely common phrase | **remove** |
| `Business insurance` | `covered` | "dog covered in mud", "insurance covered the bill" | replace → `insurance covers` |
| `Business insurance` | `protect` | "protect my dog from heat", "protect against fleas" | replace → `liability protection` |
| `Low demand` | `slow` | "slow dog", "slow walker", "slow app", "slow payout" | replace → `slow season` |
| `Discounts / promos` | `deal` | "deal with the dog", "a big deal", "deal-breaker" | **remove** |
| `Self promotion` | `neighborhood` | "neighborhood dog", "neighborhood walks" | **remove** |
| `Insights` | `data` | "mobile data", "data plan", "no data signal" | replace → `performance data` |
| `Reports` | `report` | "report a user", "report an issue", "incident report" | replace → `earnings report` |
| `Profile customization` | `profile` | "her profile said X", "check the owner's profile", "profile picture" | replace → `edit profile` |
| `Glitches / lag / bugs` | `broken` | "broken leash", "broken bone", "broken trust" | replace → `feature broken` |
| `Pick-up and drop-off` | `pick up` | "pick up after the dog", "pick up the leash" | replace → `pick up the dog` |

### High (0.80 – 0.89)

| Problem | Keyword | Fix |
|---|---|---|
| `Star ratings and reviews` | `review` | replace → `owner review` |
| `Star ratings and reviews` | `rating` | replace → `owner rating` |
| `Cancellations` | `cancel` | replace → `client cancelled` |
| `Reports` | `summary` | replace → `tax summary` |
| `Glitches / lag / bugs` | `not working` | replace → `app not working` |
| `Navigation` | `confusing` | **remove** |
| `User friendly` | `complicated` | **remove** |
| `Time off / holidays` | `unavailable` | replace → `mark unavailable` |

### Medium (0.65 – 0.79)

| Problem | Keyword | Fix |
|---|---|---|
| `Search rank` | `ranking` | **remove** |
| `Glitches / lag / bugs` | `error` | replace → `app error` |
| `Glitches / lag / bugs` | `freeze` | replace → `app freeze` |
| `Glitches / lag / bugs` | `crash` | replace → `app crash` |
| `Navigation` | `navigate` | replace → `navigate the app` |
| `Pick-up and drop-off` | `drop off` | replace → `drop off the dog` |
| `Trial` | `trial` | replace → `trial night` |
| `GPS accuracy` | `tracking` | replace → `gps tracking` |
| `Time off / holidays` | `vacation` | replace → `my vacation` |
| `Functionality` | `timezone` | replace → `timezone bug` |
| `Joining and starting on Rover` | `just started` | replace → `just started on rover` |
| `Offline support` | `offline` | replace → `offline mode` |

### Lower (0.60 – 0.64)

`Cats and kittens` / `cat`, `Refunds` / `reimburse`, `Self promotion` / `social media`, `Glitches / lag / bugs` / `lag`, `Business insurance` / `liability`, `Holidays` / `christmas`, `20% fee` / `commission`, `Faster payments` / `when do i get paid`, `Auto-correct` / `autocomplete`. See sidecar for details.

---

## 3. Gaps — missing problems

Domains the agent flagged as recurring on r/RoverPetSitting but absent from the taxonomy. These likely show up in the **Untagged** bucket today.

### High priority (≥ 0.85 confidence)

#### `Account suspension / deactivation` (theme: Business) · 0.95
Frequent and emotional topic — sitters being suspended, deactivated, or having accounts on hold. `Dropping clients` is sitter-initiated; nothing captures platform-initiated termination.

```json
{"name": "Account suspension / deactivation", "theme": "Business",
 "keywords": ["suspended", "deactivated", "account on hold", "got banned",
              "account banned", "removed from rover", "account locked", "kicked off"]}
```

#### `Rover Support quality` (theme: Business) · 0.95
One of the most frequent recurring complaints — Rover Support unresponsiveness or unhelpfulness.

```json
{"name": "Rover Support quality", "theme": "Business",
 "keywords": ["rover support", "customer service", "support team", "support agent",
              "support won't help", "support unresponsive", "contacted rover", "no response from rover"]}
```

#### `Safety and aggression incidents` (theme: Clients) · 0.95
Dog bites, dog fights, aggressive dogs, feeling unsafe in client homes. `Breeds` covers breed-related concerns, not the broader incident category.

```json
{"name": "Safety and aggression incidents", "theme": "Clients",
 "keywords": ["dog bite", "got bit", "dog attack", "dog fight", "aggressive dog",
              "feel unsafe", "scary client", "dog growled", "incident report"]}
```

#### `Lost or injured pet` (theme: Clients) · 0.90
Sitter losing a pet, pet escaping, injury/illness during a stay. Emotionally heavy and currently uncategorized.

```json
{"name": "Lost or injured pet", "theme": "Clients",
 "keywords": ["lost the dog", "dog escaped", "ran away", "got loose",
              "pet injured", "pet got hurt", "emergency vet", "pet died"]}
```

#### `Difficult clients` (theme: Clients) · 0.85
Entitled owners, rude messages, unrealistic demands, ghosting. `Dropping clients` is the action; this captures the underlying problem.

```json
{"name": "Difficult clients", "theme": "Clients",
 "keywords": ["entitled client", "entitled owner", "rude client", "rude owner",
              "demanding client", "ghosted me", "clients ghost", "owner won't respond", "bad client"]}
```

### Medium priority (0.70 – 0.84)

| Proposed problem | Theme | Confidence |
|---|---|---|
| `Burnout and mental health` | Business | 0.80 |
| `Home condition` | Preferences and rates | 0.80 |
| `Notifications` | Communication | 0.80 |
| `Scams and sketchy clients` | Clients | 0.80 |
| `Declining requests` | Requests | 0.75 |
| `Unclear owner instructions` | Communication | 0.75 |
| `Service-type preferences` | Preferences and rates | 0.70 |
| `Competition` | Business | 0.70 |

### Lower priority (0.60 – 0.69)

- `Update expectations` (Rover Cards) · 0.65 — owners demanding constant photo updates
- `Chargebacks and disputes` (Payments) · 0.65

Full keyword lists for all 15 gap proposals are in the sidecar.

---

## 4. Posts audit — skipped

Mode was `taxonomy` only. Run `/audit-tags posts` after `make export` to surface false positives, missed tags, and mis-categorized posts.

## 5. Untagged audit — skipped

Same as above. Run `/audit-tags untagged` after `make export`.

---

## Appendix — Recommended apply order

1. **Quick wins (zero-risk removals)** — delete brittle keywords with no replacement: `bother me`, `confusing`, `complicated`, `deal`, `neighborhood`, `ranking`, `autocomplete`. After: `--retag` and re-check.
2. **High-volume narrows** — replace bare-word keywords with phrasal versions: `tip` → `left a tip`, `slow` → `slow season`, `data` → `performance data`, `report` → `earnings report`, `profile` → `edit profile`, `broken` → `feature broken`, `pick up` → `pick up the dog`, `cancel` → `client cancelled`, `review` → `owner review`. These are the changes most likely to cleanly reduce the false-positive rate.
3. **Resolve the structural overlaps** — fix `off platform` dual fire, remove `cancellation policy` from Business `Cancellations`, narrow `lead time` to `long lead time`. Then re-`--retag`.
4. **Add the top-5 gap problems** — Account suspension, Rover Support quality, Safety and aggression incidents, Lost or injured pet, Difficult clients. These will likely move a meaningful chunk of the Untagged bucket into actionable categories.
5. **Re-run** `/audit-tags posts` once 1–4 land, to confirm flagged false positives are gone and to surface anything left.

---

*Generated by `/audit-tags taxonomy` on 2026-05-05. Nothing has been applied — the user reads this report, decides which suggestions to accept, edits [taxonomy.json](../taxonomy.json) by hand, then runs `python rover_sheet_dump.py --retag` to propagate.*
