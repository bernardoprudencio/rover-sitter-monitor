# Confluence Filter — Rule Derivation (2026-05-05)

Derives the eligibility filter for Confluence Research from the 75-row random sample in [2026-05-05-confluence-discovery.json](2026-05-05-confluence-discovery.json) (seed `20260505`).

Two gates, **both** must pass:

1. **Doc-type:** is this a finished research finding (vs. a plan, script, meeting note, retro, etc.)?
2. **Audience:** is this provider-relevant (sitter / walker / trainer / groomer / provider)?

## Headline observations from the discovery snapshot

- **Total rows:** 1554. **DSN: 1405 (90%)**, PSD: 149 (10%).
- **88.4% of rows have no label** — labels can BLOCK (`meeting-notes`: 128 rows) but cannot reliably ADMIT.
- The strongest doc-type signal is the **title pattern**, not labels.

### Findings vocabulary observed in titles
- `findings` / `early findings` / `findings report` / `round N findings` — 41 first-word + 37 prefix matches → strongest signal.
- Suffix `: findings`, `: write up`, `: insights` — e.g. "Google Pay Checkout: Findings", "Bookings on calendar: write Up".
- Other findings indicators: `report` (4), `insights assessment` (`insights` first-word x 18), `desk research` (3), `write[-]up` (6), `results`, `read[-]out`.

### Non-findings vocabulary observed in titles
- **Date-prefix meetings**: `2018/2019/2024/2025-…` lead 191 titles (96+36+39+20). Many also carry the `meeting-notes` label (128).
- **Preparation docs**: `script` (42 prefix), `screener` (3), `recruiting` (3), `discussion guide` (2), `research plan` (6), `study plan` (3).
- **Recurring meetings**: `Design Check-in`, `Design Sync`, `Growth ... Sync`, `Working session`.
- **Planning / vision / design**: `vision`, `proposal`, `kickoff`, `retro`, `agenda`, `OKR timelines`, `Q1 2025 Studies`.
- **Drafts / templates**: `WIP`, `(draft)`, `[TEMP …]`, `template`.

## Manual classification of the 75-row sample

`is_finding` × `is_provider` → `should_include`. Borderline = no clear signal in title alone.

| # | Title | finding | provider | include | reason |
|---|---|---|---|---|---|
| 1 | UX/Brand Guidelines proposal draft | no | — | NO | proposal/draft |
| 2 | Findings Report: Sitter Performance Score Interviews | YES | yes (sitter) | **YES** | findings + sitter |
| 3 | 2018-06-19 - Design System Sync | no (meeting) | — | NO | date-prefix meeting |
| 4 | Demographics Annual Survey | borderline | borderline | no | no findings signal |
| 5 | Writer tool implementation and process development | no | no | NO | process doc |
| 6 | Research Share-outs | no (index) | — | NO | index page |
| 7 | H1 2024 Design check-ins | no (meeting) | — | NO | meeting series |
| 8 | Resources for UX Learning | no | no | NO | resources |
| 9 | Video Chat Screens | no | borderline | NO | design doc |
| 10 | Figma for devs | no | no | NO | how-to |
| 11 | 2018-08-20 Growth Design Sync | no (meeting) | — | NO | date-prefix meeting |
| 12 | Sitter Non-response Survey - 2022, and 2026 | yes (survey results) | yes (sitter) | **YES** | sitter survey |
| 13 | Cat care details feedback survey | borderline | no (cat = owner) | NO | non-provider |
| 14 | 2019-11-12 Growth Project Sync | no (meeting) | — | NO | date-prefix meeting |
| 15 | Discovery: Three segments of users… | borderline | borderline | no | no provider term |
| 16 | 🌏 Creating a global product experience | no (vision) | — | NO | vision doc |
| 17 | M2a: modifications on web | no (spec) | no | NO | spec |
| 18 | Interview Notes: Lisa Seagrist | no (raw notes) | borderline | NO | raw notes |
| 19 | Insights Assessment — Identifying… Opportunity Areas | yes | borderline | borderline | findings, audience unclear |
| 20 | Email #08: service structure | no (comms) | — | NO | comms |
| 21 | [Internal] DEI Focus Group Feedback Survey | yes (survey) | no (internal) | NO | internal HR |
| 22 | Script: Training relationship page usability testing | no (script) | borderline | NO | script |
| 23 | Red Routes | no (design doc) | — | NO | design doc |
| 24 | 2018-06-06 - Review sitter profile/rates concepts | no (meeting) | yes | NO | date-prefix meeting |
| 25 | Strengthening the Data & Insights partnership | no (vision) | — | NO | vision |
| 26 | 2025-01-16 Design Check-in | no (meeting) | — | NO | date-prefix meeting |
| 27 | Rover History | no | — | NO | history |
| 28 | Design exploration: unified modification model… | no (exploration) | borderline | NO | design exploration |
| 29 | Upwork | no | — | NO | misc |
| 30 | Findings: Travel Time Distance | yes | borderline | borderline | findings, audience unclear |
| 31 | Conjoint Design_Options | no (design) | — | NO | design options |
| 32 | Social Artifacts Post Experiment Interviews | borderline | borderline | borderline | unclear |
| 33 | Product Partners | no (org) | — | NO | org |
| 34 | Photo Gallery Meeting Notes | no (meeting) | — | NO | meeting notes |
| 35 | Findings: Groomer sign-up usability | YES | yes (groomer) | **YES** | findings + groomer |
| 36 | [TEMP FOR SPLITTING PURPOSES] Style guide iteration | no (draft) | no | NO | draft |
| 37 | UX Hiring Interview Process | no (HR) | no | NO | HR |
| 38 | 2018-02-26 Decoupling follow-up | no (meeting) | — | NO | date-prefix meeting |
| 39 | Bookings on calendar: write Up | yes (write-up) | borderline | borderline | findings, audience unclear |
| 40 | Script - Regular Use Group: Sitter Scores Discovery Interviews | no (script) | yes | NO | script |
| 41 | 2024-09-16 Design Check-in | no (meeting) | — | NO | date-prefix meeting |
| 42 | Script: Gingr exploration with New-to-Rover owners | no (script) | no | NO | script |
| 43 | Gingr experience exploration w/ new-to-Rover owners | borderline | no (owners) | NO | seeker focus |
| 44 | Q1 2025 Studies | no (index) | — | NO | index |
| 45 | January Ideation | no (planning) | — | NO | planning |
| 46 | 2019-07-01 | no (meeting) | — | NO | date-prefix meeting |
| 47 | Interview notes: Catherine George (4/1/2022) | no (raw notes) | borderline | NO | raw notes |
| 48 | Script: Rover Card migration validation testing | no (script) | borderline | NO | script |
| 49 | Dog walking flexible services concept test | borderline | yes (walker) | borderline | unclear, but walker |
| 50 | Matteo Q2 2021 OKR Timelines | no (OKR) | — | NO | OKR |
| 51 | Findings: SMS comparative testing | yes | borderline | borderline | findings, audience unclear |
| 52 | Gino OKR Timelines | no (OKR) | — | NO | OKR |
| 53 | Public star rating usability testing | borderline | yes (sitter ratings) | borderline | unclear if findings |
| 54 | Script: Paid M&G interviews with sitters | no (script) | yes | NO | script |
| 55 | Early findings: New-to-Rover groomers | YES | yes (groomer) | **YES** | findings + groomer |
| 56 | Conjoint Survey: Alt. Monetization [United States] | borderline | borderline | borderline | unclear |
| 57 | Resources - Articles and Conferences | no | — | NO | resources |
| 58 | Rate ordering in ledgers and settings | no (spec) | yes (PSD) | NO | spec, PSD but spec |
| 59 | Google Pay Checkout: Findings | yes (suffix) | borderline | borderline | findings, audience unclear |
| 60 | Interview notes: Judy Weir 8/23/2022 | no (raw notes) | borderline | NO | raw notes |
| 61 | Research Plan: Cat in a Flat: Validating Assumptions | no (plan) | borderline | NO | research plan |
| 62 | Training Offerings Landing Page Usability | borderline | borderline | borderline | unclear |
| 63 | Q&A Reflection on the GCA 28 days test | borderline | borderline | borderline | unclear |
| 64 | Interview Notes: Michael Coelho | no (raw notes) | borderline | NO | raw notes |
| 65 | Script: Training owner usability - contact to book | no (script) | no (owner) | NO | script + owner |
| 66 | 2024-05-06 Design Check-in | no (meeting) | — | NO | date-prefix meeting |
| 67 | Session Notes: Chad Carmicheal (3/4/2022) | no (raw notes) | borderline | NO | session notes |
| 68 | Script: Cat-specific Rover Cards testing | no (script) | no (cat owners) | NO | script + cat |
| 69 | Findings: SSS Safety Quiz | YES | borderline | borderline | findings, audience unclear |
| 70 | Findings: HVS early experiences and characteristics | YES | borderline | borderline | findings, audience unclear |
| 71 | M&Gs | no (index) | yes | NO | index |
| 72 | Acceleration #4: Sitter Self-Promotion Hub (vision work) | no (vision) | yes | NO | vision |
| 73 | Interview notes: Holly Carpentier 8/22/2022 | no (raw notes) | borderline | NO | raw notes |
| 74 | SMS revisions comparative testing | borderline | borderline | borderline | unclear |
| 75 | Kibble Design System: Shadow Elevation Guide for UI Elements - WIP | no (WIP) | no | NO | WIP |

**Tally:**
- Clear `YES` (definite include): **4** rows (#2, 12, 35, 55) ≈ 5%
- Borderline / depends-on-body: ~12 rows ≈ 16%
- Clear `NO`: ~59 rows ≈ 79%

The filter must aggressively exclude (~80% of pages) while reliably catching the clear findings. Body-content checks (provider terms, findings vocabulary) will lift recall on the borderline cases.

## Derived rules

### Doc-type — non-findings BLOCK list (any match → reject)

**Title regex** (case-insensitive, applied to full title):
- `^\d{4}[-/]\d{1,2}[-/]\d{1,2}\b` — date-prefix meetings (191 rows)
- `^(script|screener|recruiting|research\s+plan|study\s+plan|discussion\s+guide|conjoint\s+design|design\s+exploration|vision|proposal|draft|wip|temp|template|agenda|kick[\s-]?off|retro|rfc|spec|standup|sync|meeting\s+notes|session\s+notes|test\s+session\s+notes|interview\s+notes|interview\s+transcript|notes\s+from|okrs?|q[1-4]\s+\d{4}|january\s+ideation|red\s+routes|rover\s+history|product\s+partners|resources?(\s|[-:])|fonts?$|figma\b)\b`
- `\b(meeting\s+notes|design\s+check[\s-]?in|design\s+sync|growth\s+(design\s+|project\s+)?sync|working\s+session|stand[\s-]?up|all[\s-]?hands|kick[\s-]?off|okr\s+timelines?|hiring\s+interview)\b`
- `\bwip\b|\(wip\)|\(draft\)|\[temp\b|\btemplate\b|\bplaceholder\b`

**Label set** (any match → reject):
- `meeting-notes`, `okrs`, `projectplan`, `project`, `org-chart`, `file-list`, `figma`, `kb-how-to-article`

### Doc-type — findings ADMIT list (must match)

**Title regex** (case-insensitive, applied to full title):
- `^(findings(\s+report)?|early\s+findings|round\s+\d+\s+findings|key\s+findings|insights?(\s+assessment)?|key\s+insights?|read[\s-]?out|report|reports|results|write[\s-]?up|desk\s+research|survey\s+results|study\s+results)\b`
- `:\s*(findings|write[\s-]?up|insights?|results|report)\s*$` — suffix form (catches "Google Pay Checkout: Findings", "Bookings on calendar: write Up")

**Title contains "survey" with provider term** — admits sitter/walker/groomer surveys (e.g. "Sitter Non-response Survey"):
- `\b(sitter|walker|trainer|groomer|provider|host)\b` AND `\bsurvey\b` in title.

### Audience filter — provider relevance

After doc-type passes:
- **PSD space** → admit by default (provider-by-definition).
- **DSN space** → require `\b(sitter|walker|trainer|groomer|provider|host|hosting|sitting|boarding|daycare|drop[\s-]?in|drop[\s-]?off|m&g|meet\s+and\s+greet|caregiver|pet\s+care\s+professional|pet\s+pro|pet\s+sitter|dog\s+walker|dog\s+walking|cat\s+sitter|service\s+provider)\b` in title OR body.

### Reason codes (`FilterReason` column)

- `""` (empty) — eligible.
- `non_findings_label:<label>` — blocked by label blocklist.
- `non_findings_title:<snippet>` — blocked by title blocklist regex.
- `no_findings_signal` — title doesn't match the findings whitelist.
- `non_provider:dsn_no_provider_terms` — DSN page with no provider term in title or body.
- `bypassed` — `--no-filter` mode.

### Order of evaluation

1. `--no-filter` bypass.
2. Label blocklist.
3. Title blocklist regex.
4. Findings whitelist regex.
5. Audience: PSD → admit; DSN → require provider terms.

## Expected behavior on the sample

Estimating on titles + assuming bodies of `Findings:`/`Survey` rows mention provider terms:

- Definite admits: 4 (#2, 12, 35, 55) → all 4 reach Phase 4 audit.
- Likely admits if body has provider terms: #19, #30, #39, #51, #59, #69, #70 (Findings/Insights titles) → 7 more if their bodies mention sitters/groomers/etc.
- Total expected admits in sample: 4–11 of 75 rows ≈ 5–15%.
- Total expected admits in full sheet: ~80–230 of 1554 rows.

If the audit shows we're under-admitting genuine provider findings, the lever is to add more title prefixes (e.g. `discovery:`, `comparative testing:`) to the whitelist.
