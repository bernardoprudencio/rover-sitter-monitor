# Confluence Filter Audit — Round 1 (2026-05-05)

## Run Summary

| | |
|---|---|
| **Date** | 2026-05-05 (UTC) |
| **Mode** | First-round audit of `evaluate_eligibility` filter |
| **Reviewer** | Claude Code subagent |
| **Inputs** | [rules derivation](2026-05-05-confluence-filter-rules-derivation.md) + 100-row stratified sample (50 included / 50 excluded) |
| **Filter under test** | `rover_confluence_dump.py:132` `evaluate_eligibility()` |
| **Sheet stats** | 1554 total rows, **70 eligible**, 1484 excluded |
| **Sample seed** | `20260505` |
| **Sidecar** | [2026-05-05-confluence-filter-round1.json](2026-05-05-confluence-filter-round1.json) |

---

## Headline: 84.0% inclusion precision, 96.0% exclusion precision

| Verdict | Count | % of bucket | Notes |
|---|---|---|---|
| `correct_include` | **42** | 84.0% of 50 | filter said yes, audit agrees |
| `false_positive`  | **8**  | 16.0% of 50 | filter said yes, audit says no |
| `correct_exclude` | **48** | 96.0% of 50 | filter said no, audit agrees |
| `false_negative`  | **2**  |  4.0% of 50 | filter said no, audit says yes |
| **total** | **100** | — | — |

| Metric | Value | 95% Wilson CI | n |
|---|---|---|---|
| **Inclusion precision** | **0.840** | 0.7149 – 0.9166 | 50 |
| **Exclusion precision** | **0.960** | 0.8654 – 0.9890 | 50 |

**Verdict against project bar (`correct ≥ 88%, FP ≤ 6%`): inclusion precision misses by 4.0 pp** (84% vs 88% target; 16% FP vs 6% target). Exclusion precision exceeds the bar (96%). Recall (extrapolated from FN rate × excluded pool) suggests the filter loses roughly **4% × 1484 ≈ 60 eligible pages** in the excluded pool — small absolute number but worth one or two surgical adds. The dominant error mode is **the provider-survey escape hatch admitting study plans, checklists, and templates**.

---

## Inclusion FP cluster breakdown

Sorted by count.

### 1. Provider-survey escape hatch admits PLANS / CHECKLISTS / TEMPLATES — 6 of 8 FPs (75% of all FPs)

`PROVIDER_SURVEY_RE` (`rover_confluence_dump.py:117`) matches `<provider>...survey` in the title and bypasses the doc-type whitelist. Six FPs in this audit are titles where that pattern fires on a **survey-planning artifact** (RACI checklist, questions to add, draft survey), not a write-up of survey results.

| Title | Excerpt giveaway |
|---|---|
| CSD sitter email survey checklist - Q4 2025 | "Action item / Person and RACI role / Timing… complete Submit request to survey council" |
| Sitter non-response survey - Feb 2026 | RACI checklist, identical pattern |
| Checklist: Provider pricing preferences survey | RACI checklist, identical pattern |
| Sitter Survey Request: Promotion & Social Media | "We add questions pertaining to…" — request for the survey, not results |
| Sitter Preferences Survey | "Background / We know sitters have a lot of preferences" — goals, no results |
| Sitter satisfaction survey: requesting ad-hoc/deep-dive questions | "we include a 'deep dive' section" — question-submission template |
| Groomer pricing survey [draft] | "Status Planning" + "[draft]" in title |

**Fix (highest leverage, ranked by simplicity):**

1. **Block `checklist` and `request` anywhere in title.** Add `\bchecklist\b|\brequest\b` to `NON_FINDINGS_TITLE_RE` (`:86`). Captures 4 of the 6 FPs at near-zero recall risk — a "checklist:" page is essentially never a write-up.
2. **Recognise `[draft]` as well as `(draft)`.** `NON_FINDINGS_TITLE_RE` currently has `\(draft\)` (parens only). Extend to `[\(\[]draft[\)\]]`. Captures the groomer pricing FP and is forward-compatible.
3. **Body-content gate on the provider-survey escape hatch.** Today `PROVIDER_SURVEY_RE` admits with no body check (line 155: `FINDINGS_TITLE_RE.search(title_l) or PROVIDER_SURVEY_RE.search(title_l)`). Replace with: if the title only matches `PROVIDER_SURVEY_RE` (not `FINDINGS_TITLE_RE`), require body to contain at least one of `summary|tl;dr|key findings|highlights|key insights|takeaways`. RACI-checklist excerpts contain none of those. Captures `Sitter Preferences Survey` and the remaining survey-planning FPs.

Expected delta: inclusion precision **0.84 → ~0.96** (recovers 6 of 8 FPs); recall risk near-zero on the sample's correct-include set (genuine sitter survey results all have summary/tl;dr/key findings).

### 2. `Findings: Training owners …` — provider term in body but study is owner-centric — 1 FP

`Findings: Training owners bundle exploration study` — title says "owners", excerpt is mostly about owners. The body contains "trainer" once because the owner is *contacting* a trainer, but the audience of the study is owners.

**Fix:** Stricter audience filter — require provider term in **title**, OR require provider term to appear ≥2 times in body. `PROVIDER_TERMS_RE.search(haystack)` currently requires 1 hit anywhere. Lower priority — this is 1 of 50 in the sample, and the change risks losing legitimate provider studies that mention the term once.

### 3. `Survey Request:` admitted via FINDINGS_TITLE_RE — 1 FP

Already captured by Fix 1.1 above (`\brequest\b` block).

---

## Exclusion FN cluster breakdown

Only 2 false negatives across 50 excluded — exclusion precision is healthy.

### 1. `Acceleration #N:` prefix not whitelisted — 1 FN

`Acceleration #3: Sitter self-promotion and sharing behaviors & Concept feedback`. Excerpt opens with "Executive Summary: Sitters were active on social media platforms…" — clearly a finished research finding. Filter rejected with `no_findings_signal` because `Acceleration #` is not in `FINDINGS_TITLE_RE`.

**Fix:** Add `acceleration\s+#?\d+` to `FINDINGS_TITLE_RE` prefix branch (`:108`). Risk: low — the term is internal Rover lingo for finished research artifacts.

### 2. Filter blocked `Write Up: Star Rating in Search` because the body it sampled lacked provider terms — 1 FN

`Write Up: Star Rating in Search`. Suffix-form findings, full body does mention sitter context — but `evaluate_eligibility` sees only the **excerpt** (truncated to 500 chars) on the `--retag` path. Confirmed at `rover_confluence_dump.py:704`:

```python
# Use excerpt as proxy for body (full body isn't stored). 500 chars
# of plain text is usually enough to spot provider terms; if not,
# body-less FNs will surface in the audit and we can re-fetch.
eligible, reason = evaluate_eligibility(title, excerpt, labels, space)
```

The fresh-fetch path (`:399`) correctly passes `plain` (full body). The `--retag` path uses `excerpt`. This is a known TODO — it's surfacing now.

**Fix:** Two options ranked by cost:
- **(low cost)** Concatenate themes+problems columns into the haystack on the retag path. The Star Rating in Search row has themes "Business" and problem "Star ratings and reviews" — neither contains a provider term, so this fix alone wouldn't catch this row. But more generally, themes/problems often contain provider context.
- **(correct cost)** Re-fetch the full body during `--retag` for any row whose excerpt hits the audience filter as `dsn_no_provider_terms`. Two-pass: first run with excerpt, then for rejected-on-audience rows, fetch full body via Confluence API and re-run. Recovers this FN class without inflating the routine path.

Expected delta on FN: 0.04 → ~0.02 (recovers 1 of 2 FNs); modest because exclusion precision is already 96%.

---

## What's working

- **`Findings:` / `Findings Report:` / `Round N Findings:` prefix** — 26 of 42 correct admits use this exact pattern. Zero FPs from this branch.
- **Suffix form `: Findings` / `: Write Up` / `: Report`** — admits `Pet tracker sitter focus group: Findings`, `Bookings on calendar: write Up`, `Special needs sitter preferences: findings`. 5 correct admits, zero FPs.
- **`Write Up` / `Write-up` prefix** — correctly admits Bernardo's research write-ups.
- **PSD audience bypass** — 4 PSD rows in the included bucket, all correct admits (the `space == "PSD"` short-circuit at `:159` is doing the right job).
- **NON_FINDINGS_TITLE_RE date-prefix branch** — caught 3 `2024-XX-XX Design Check-in` rows in the excluded sample, zero misclassifications.
- **`script:` / `recruiting` / `template` / `interview notes` blocklist** — 6 correct excludes from these prefixes; no FNs in this audit indicate over-blocking.
- **Label blocklist** — `meeting-notes` and `okrs` labels correctly blocked 2 rows even though the title was salvageable on its own.

---

## Round 2 plan

Targets: inclusion precision **≥ 0.92** (FP ≤ 8% to catch the worst of the survey-checklist cluster while staying conservative on body-content checks); exclusion precision **≥ 0.96** (no regression).

Levers ranked by expected impact, all in `rover_confluence_dump.py`:

### Lever A — Block `checklist` / `request` in title (highest impact)

```python
# NON_FINDINGS_TITLE_RE (line 86) — append to the "Recurring meeting markers anywhere" branch
... r"|\bchecklist\b|\bsurvey\s+request\b"
```

- **Captures:** FPs `CSD sitter email survey checklist`, `Checklist: Provider pricing preferences survey`, `Sitter Survey Request: Promotion & Social Media`. Possibly `Sitter satisfaction survey: requesting ad-hoc/deep-dive questions` if we extend to `\brequesting\b` — but that's higher recall risk; prefer scoped `survey request`.
- **Expected delta:** 3 of 8 FPs eliminated; inclusion precision 0.84 → ~0.90.
- **Recall risk:** near-zero. No correct-admit row in the sample has `checklist` or `survey request` in title.

### Lever B — Recognise `[draft]` alongside `(draft)`

```python
# NON_FINDINGS_TITLE_RE (line 86), in the WIP/draft markers branch:
... r"|\(wip\)|\bwip\b|[\(\[]draft[\)\]]|\[temp\b|\btemplate\b|\bplaceholder\b"
```

- **Captures:** `Groomer pricing survey [draft]`.
- **Expected delta:** 1 FP eliminated; cumulative ~0.92.
- **Recall risk:** zero. `[draft]` is a strict negative signal.

### Lever C — Body-content gate on the provider-survey escape hatch

Modify `evaluate_eligibility` (line 155) so that when only `PROVIDER_SURVEY_RE` matches (not `FINDINGS_TITLE_RE`), the body must contain a findings-vocabulary term:

```python
FINDINGS_BODY_RE = re.compile(
    r"\b(summary|tl;?dr|key\s+findings|highlights|key\s+insights|takeaways|"
    r"key\s+takeaways|recommendations|results)\b",
    re.IGNORECASE,
)

# replace line 155:
title_is_findings = bool(FINDINGS_TITLE_RE.search(title_l))
title_is_provider_survey = bool(PROVIDER_SURVEY_RE.search(title_l))
if not (title_is_findings or title_is_provider_survey):
    return False, "no_findings_signal"
if title_is_provider_survey and not title_is_findings:
    if not FINDINGS_BODY_RE.search(body or ""):
        return False, "provider_survey_no_findings_body"
```

- **Captures:** `Sitter Preferences Survey`, `Sitter non-response survey - Feb 2026` (RACI excerpts contain none of summary/tl;dr/key findings).
- **Expected delta:** 2 more FPs eliminated; cumulative ~0.96.
- **Recall risk:** modest. Need to verify all current correct-admit `<provider> Survey` rows have a findings vocab term in body. Spot-check on the existing 70 eligible: row 5 (`Sitter satisfaction biannual survey`) has "Background"/"primary owner" — would NOT match the proposed FINDINGS_BODY_RE. Risk of breaking ~5–10 currently-eligible survey rows. **Run with `--dry-run` first; if recall regresses, widen the body whitelist to include `background|goals|learning objectives|stakeholders|results` (the latter is already there).** Or apply only when the title regex is the bare `<provider> Survey` form (no findings/results word).

### Lever D — Whitelist `Acceleration #N:` titles (recall recovery)

```python
# FINDINGS_TITLE_RE (line 107), append to the prefix alternation:
... r"|acceleration\s+#?\d+"
```

- **Captures:** `Acceleration #3: Sitter self-promotion`.
- **Expected delta:** 1 FN recovered; exclusion precision unchanged at 0.96 (this is a recall lever, not a precision one).
- **Recall risk:** acceptable. `Acceleration #N` is internal Rover terminology and the body in this case is a finished write-up.

### Lever E — Re-fetch full body for `dsn_no_provider_terms` rejections on `--retag`

Modify the `--retag` block (`rover_confluence_dump.py:704`) so that rows rejected with `non_provider:dsn_no_provider_terms` trigger a single GET against `/wiki/api/v2/pages/{id}?body-format=storage` and re-run `evaluate_eligibility` with the full body. This fixes `Write Up: Star Rating in Search` and any similar truncation-window FN.

- **Expected delta:** 1 FN recovered; minor cost (one GET per ~20–60 rejected-on-audience rows per retag). Worth it.

### Skip / observe (Round 2 deferred)

- **`Findings: Training owners …` audience strictness** — only 1 FP; raising to ≥2 provider-term hits in body risks recall on legitimate sparse mentions. Park.
- **`Sitter satisfaction survey: requesting ad-hoc questions`** — captured by Lever A's `\bsurvey\s+request\b` if we generalize to `\brequesting\b`, but cleaner to handle via Lever C body-content gate.

---

## Sample summary

- **Provider-survey escape hatch** is the dominant FP source — 6 of 8 inclusion FPs.
- **Date-prefix block** and **non-findings prefix block** are working as designed (zero FPs from these branches).
- **PSD bypass** is correct on the 4 PSD admits; no PSD FPs.
- **Truncated-body retag path** is the only systemic FN cause; fixed by re-fetching when audience is the rejection reason.

After Levers A–E, expect inclusion precision ≈ 0.94–0.96, exclusion precision ≥ 0.96, and the project bar (≥ 88% / ≤ 6% FP) cleared on inclusion.
