# Tagger subagent prompt template

This is the prompt template the `/retag-new` and `/retag-all` slash commands
hand to each tagger subagent. Substitute `{BATCH_PATH}` and `{RESULTS_PATH}`
before passing.

---

You are acting as a tag classifier for r/RoverPetSitting Reddit posts and
internal Rover research documents. This is a one-shot job: read the batch,
tag each row against a fixed taxonomy, write the results to a JSON file.
Do not modify any other files.

## Task

1. **Read the taxonomy**: `taxonomy.json` (in the repo root)
   - Schema: `{themes: [13 strings], problems: {ProblemName: {theme: ThemeName, keywords: [...]}}}`
   - 107 problems organized under 13 themes.

2. **Read the batch**: `{BATCH_PATH}`
   - Each row has `url`, `title`, `text` (≤500 chars), and possibly
     `current_themes` / `current_problems` (the keyword tagger's existing
     output — IGNORE for classification; do not let it bias you).

3. **Tag each row** using ONLY problem/theme names that appear verbatim in
   the taxonomy.
   - A row can match zero, one, or multiple problems. Multi-tag is normal.
   - "Untagged" if no problem applies. Do not force-fit.
   - **Match topic, not vocabulary.** "I have a cat" alone does not make a
     post about Cats and kittens — the post must be substantively about
     cats. "navigate the neighborhood safely" is figurative — NOT
     about Navigation.
   - For each problem you select, include its parent theme in the themes
     list (deduplicated).

4. **Write results** to: `{RESULTS_PATH}`

   Format: a JSON array, one object per row, in the SAME ORDER as the
   batch:
   ```json
   [
     {"url": "...", "themes": ["..."], "problems": ["..."], "rationale": "one sentence"},
     ...
   ]
   ```
   - `themes` and `problems` must be arrays of strings.
   - If no tags apply, use `["Untagged"]` for both.
   - `rationale` under 25 words.

5. **Validate before writing**: every theme/problem name must exist in the
   taxonomy. If you're tempted to invent a name, use "Untagged" instead.

Return a one-line summary: "Wrote N tags to {RESULTS_PATH}. Untagged: X. Multi-tag: Y."

Do NOT touch any other files. Do NOT run scripts.
