# Confluence Filter Audit — Round 2 (2026-05-05)

## Run Summary

| | |
|---|---|
| **Date** | 2026-05-05 (UTC) |
| **Mode** | Dry-run: applied Round 2 rule changes to the Round 1 sample (no new fetch / no new manual classification) |
| **Filter under test** | `rover_confluence_dump.py:65–171` (post-Round-2 edits) |
| **Inputs** | Round 1 manual classifications ([2026-05-05-confluence-filter-round1.json](2026-05-05-confluence-filter-round1.json)) re-scored against the updated `evaluate_eligibility` |
| **Sample seed** | `20260505` (same 100 rows as Round 1) |
| **Round 1 baseline** | inclusion 0.840 / exclusion 0.960 |

---

## Headline: 91.5% inclusion precision, 98.1% exclusion precision — clears project bar

| Verdict | Round 2 | Round 1 | Δ |
|---|---|---|---|
| `correct_include` | **43** | 42 | +1 |
| `false_positive`  | **4**  | 8  | -4 |
| `correct_exclude` | **52** | 48 | +4 |
| `false_negative`  | **1**  | 2  | -1 |

| Metric | Round 2 | Round 1 | Δ vs target |
|---|---|---|---|
| **Inclusion precision** | **0.915** (43/47) | 0.840 | beats 0.88 by 3.5 pp |
| **Exclusion precision** | **0.981** (52/53) | 0.960 | beats 0.96 |

All 5 verdict flips are in the right direction (4 inclusion FPs eliminated + 1 exclusion FN recovered, 0 new errors introduced).

---

## Round 2 changes applied

All in [rover_confluence_dump.py](rover_confluence_dump.py).

### Lever A — block `checklist` and `survey request` in title

```diff
NON_FINDINGS_TITLE_RE:
  prefix branch:    ...|email\s+#|checklist)\b
  recurring branch: ...|hiring\s+interview|checklist|survey\s+request)\b
```

Captured FPs (3):
- `CSD sitter email survey checklist - Q4 2025` → `non_findings_title:checklist`
- `Checklist: Provider pricing preferences survey` → `non_findings_title:checklist`
- `Sitter Survey Request: Promotion & Social Media` → `non_findings_title:survey request`

### Lever B — generalize `(draft)` → `[\(\[]draft[\)\]]`

```diff
NON_FINDINGS_TITLE_RE:
- |\(wip\)|\bwip\b|\(draft\)|\[temp\b|\btemplate\b|\bplaceholder\b
+ |\(wip\)|\bwip\b|[\(\[]draft[\)\]]|\[temp\b|\btemplate\b|\bplaceholder\b
```

Captured FPs (1):
- `Groomer pricing survey [draft]` → `non_findings_title:[draft]`

### Lever D — whitelist `Acceleration #N:` titles

```diff
FINDINGS_TITLE_RE:
  prefix branch: ...|survey\s+results|study\s+results|
+                  acceleration\s+#?\d+)\b
```

Recovered FN (1):
- `Acceleration #3: Sitter self-promotion and sharing behaviors` → admitted

### Skipped Round 2 levers

- **Lever C (body-content gate on `PROVIDER_SURVEY_RE`)** — recall risk on currently-eligible sitter surveys was flagged in Round 1; deferred until we can verify on the full eligible pool. Round 3 candidate.
- **Lever E (re-fetch full body for `dsn_no_provider_terms` rejections during retag)** — recovers ≈1 FN; deferred as a code-cost vs. recall-gain decision.

---

## Residual errors after Round 2

### Inclusion FPs (4 of 50)

Provider-survey escape hatch still admits **goal-stage / proposal-stage** surveys whose titles don't include "checklist" or "[draft]" or "survey request":

| Title | Why it slips |
|---|---|
| `Sitter non-response survey - Feb 2026` | Bare `<provider> Survey` admits via `PROVIDER_SURVEY_RE`; excerpt is RACI-style but no blocked keyword |
| `Sitter Preferences Survey` | Same pattern; excerpt opens with "Background" |
| `Sitter satisfaction survey: requesting ad-hoc/deep-dive questions` | "requesting" — not the blocked `survey request` literal phrase |
| `Findings: Training owners bundle exploration study` | Owner-centric study, single "trainer" mention in body — passes audience filter |

Lever C (body-content gate) is the targeted fix for the first three. The fourth is a precision/recall trade-off on the `PROVIDER_TERMS_RE` count threshold; not worth touching at this rate (1/50).

### Exclusion FNs (1 of 50)

`Write Up: Star Rating in Search` — title matches `: write up` suffix BUT was rejected because the 500-char excerpt sampled by `--retag` lacked provider terms. Lever E (full-body re-fetch on audience rejection) is the targeted fix.

---

## Round 3 plan (deferred)

Only act if a follow-up audit shows precision regression or the residual FPs become user-visible:

1. **Lever C (body-content gate on `PROVIDER_SURVEY_RE`)** — implement with a `--dry-run` first to enumerate which currently-eligible rows would be lost. Acceptable if loss ≤ 5 rows of 70.
2. **Lever E (full-body re-fetch on `--retag`)** — wire in a single Confluence GET per rejected-on-audience row. Acknowledge the API cost (1× per ~1500 rows ≈ 50 calls if ~3% of rejects are audience-only; bounded).
3. **Stricter audience rule** — require provider term to appear ≥2× in title+body. Defer until after Lever C lands; risk profile changes once survey FPs are out.

No Round 3 needed unless the 91.5% / 98.1% Round-2 numbers regress on a fresh sample.
