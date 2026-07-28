# Locked Rates VoC analysis — subagent prompt template

Prompt handed to each W2 (core) / W4 (supporting) analysis subagent. Substitute
`{BATCH_PATH}` and `{RESULTS_PATH}` before passing. Adapted from
`scripts/star_sitter/analysis_prompt.md`.

---

You are analyzing r/RoverPetSitting Reddit posts about how Rover sitters manage
their **rates** — especially **Locked Rates**, the feature that lets a sitter
lock/unlock the price for a repeat client so it stays fixed between bookings.
Rover is weighing whether to evolve Locked Rates from a binary lock/unlock into
**granular per-client rate management** — more control over editing rates,
visibility into what each client sees, and general edits (not just lock vs.
unlock). Your job is to read a batch of posts and extract the Voice of the
Customer — how sitters (and some pet owners) actually feel and what they
struggle with around setting, locking, changing, and seeing rates. One-shot job:
read the batch, analyze each row, write JSON. Do not modify any other files. Do
not run scripts.

## Task

1. **Read the batch**: `{BATCH_PATH}`
   - Each row has `id`, `url`, `title`, `text` (≤500 chars — a truncated post
     body), `date`, and possibly `current_problems`. `text` may be empty for
     image/link posts; analyze from the `title` in that case and set
     `"text_available": false`.

2. **Analyze each row**. Produce, per post:
   - `sentiment`: one of `positive`, `negative`, `mixed`, `neutral` — the
     author's stance toward managing/locking rates on Rover.
   - `signal`: one sentence (≤25 words) capturing the VoC point — the concrete
     pain, praise, question, or desire expressed.
   - `quote`: the single most representative **verbatim** span copied exactly
     from `title` or `text` (≤200 chars, no paraphrasing, no ellipsis unless it
     is in the source). If nothing quotable, use `""`.
   - `theme_hint`: 1–2 labels from this list that best fit (or `["other"]`):
     `cant-edit-locked-rate`, `unclear-how-to-lock-unlock`,
     `client-visibility-confusion`, `stuck-old-rate-repeat-client`,
     `wants-per-client-control`, `holiday-seasonal-rate-gap`,
     `unexpected-price-change-dispute`, `wants-bulk-or-granular-edit`,
     `rate-sync-or-bug`, `praise`, `other`.
   - `relevance`: `high` / `medium` / `low` — how directly the post speaks to
     locking/managing rates for clients (vs. a passing mention of price).

3. **Rules**
   - Quote must be an exact substring of the source text/title. Verify before
     writing. If you cannot copy it exactly, set `quote` to `""`.
   - Judge the topic, not vocabulary. A post that mentions "lock" about a lockbox
     or "block" about a calendar, or just names a price in passing, is
     `relevance: low` (or `theme_hint: ["other"]`).
   - Do not invent theme labels outside the list above.

4. **Write results** to `{RESULTS_PATH}`: a JSON array, one object per row, in
   the SAME ORDER as the batch:
   ```json
   [
     {"id":"...","url":"...","date":"...","sentiment":"negative",
      "signal":"...","quote":"...","theme_hint":["cant-edit-locked-rate"],
      "relevance":"high","text_available":true},
     ...
   ]
   ```

5. Return a one-line summary: "Wrote N rows to {RESULTS_PATH}. high=… neg=… pos=…".

Do NOT touch any other files. Do NOT run scripts.
