# Star Sitter VoC analysis — subagent prompt template

Prompt handed to each W2 (core) / W4 (supporting) analysis subagent. Substitute
`{BATCH_PATH}` and `{RESULTS_PATH}` before passing. Adapted from
`scripts/retag/subagent_prompt.md`.

---

You are analyzing r/RoverPetSitting Reddit posts about Rover's **Star Sitter**
program (a badge sitters earn for meeting monthly performance criteria). Rover
is weighing whether to turn Star Sitter from a single badge into a **tiered
loyalty program**. Your job is to read a batch of posts and extract the Voice of
the Customer — how sitters (and some pet owners) actually feel and what they
struggle with. One-shot job: read the batch, analyze each row, write JSON. Do
not modify any other files. Do not run scripts.

## Task

1. **Read the batch**: `{BATCH_PATH}`
   - Each row has `id`, `url`, `title`, `text` (≤500 chars — a truncated post
     body), `date`, and possibly `current_problems`. `text` may be empty for
     image/link posts; analyze from the `title` in that case and set
     `"text_available": false`.

2. **Analyze each row**. Produce, per post:
   - `sentiment`: one of `positive`, `negative`, `mixed`, `neutral` — the
     author's stance toward the Star Sitter program / their standing.
   - `signal`: one sentence (≤25 words) capturing the VoC point — the concrete
     pain, praise, question, or desire expressed.
   - `quote`: the single most representative **verbatim** span copied exactly
     from `title` or `text` (≤200 chars, no paraphrasing, no ellipsis unless it
     is in the source). If nothing quotable, use `""`.
   - `theme_hint`: 1–2 labels from this list that best fit (or `["other"]`):
     `opaque-criteria`, `all-or-nothing-threshold`, `loss-anxiety`,
     `weak-reward`, `tied-to-search-and-bookings`, `new-sitter-disadvantage`,
     `wants-tiers-or-progression`, `wants-transparency`, `owner-perception`,
     `praise`, `other`.
   - `relevance`: `high` / `medium` / `low` — how directly the post speaks to
     the Star Sitter program itself (vs. a passing mention).

3. **Rules**
   - Quote must be an exact substring of the source text/title. Verify before
     writing. If you cannot copy it exactly, set `quote` to `""`.
   - Judge the topic, not vocabulary. A post that merely says "my star sitter"
     in passing while asking an unrelated question is `relevance: low`.
   - Do not invent theme labels outside the list above.

4. **Write results** to `{RESULTS_PATH}`: a JSON array, one object per row, in
   the SAME ORDER as the batch:
   ```json
   [
     {"id":"...","url":"...","date":"...","sentiment":"negative",
      "signal":"...","quote":"...","theme_hint":["loss-anxiety"],
      "relevance":"high","text_available":true},
     ...
   ]
   ```

5. Return a one-line summary: "Wrote N rows to {RESULTS_PATH}. high=… neg=… pos=…".

Do NOT touch any other files. Do NOT run scripts.
