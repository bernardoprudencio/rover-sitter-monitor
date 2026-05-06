"""LLM tagger using the Anthropic API with prompt-cached taxonomy.

The taxonomy is ~17KB and stable — perfect for ephemeral cache. After the
first call in a 5-min window, every subsequent call reads it at cache-read
pricing instead of full input pricing.
"""
from __future__ import annotations

import json
import os
import time
from dataclasses import dataclass, field
from pathlib import Path

import anthropic

REPO_ROOT = Path(__file__).resolve().parents[3]
TAXONOMY_PATH = REPO_ROOT / "taxonomy.json"

DEFAULT_MODEL = "claude-haiku-4-5"


def _build_system_prompt(taxonomy: dict) -> str:
    return f"""You are a tag classifier for r/RoverPetSitting Reddit posts and Rover internal research documents. Your job is to assign zero or more (theme, problem) pairs from a fixed taxonomy.

TAXONOMY (authoritative — do not invent themes or problems not listed here):
{json.dumps(taxonomy, indent=2)}

RULES:
- Use only theme/problem names that appear verbatim in the taxonomy above.
- A post can match zero, one, or multiple problems. Multi-tag is normal.
- "Untagged" if no problem applies. Do not force-fit.
- Match topic, not vocabulary. "I have a cat" alone does not make a post about Cats and kittens — the post must be substantively about cats.
- For each problem you select, include its parent theme in the themes list (deduplicated).
- Output JSON only. No prose, no markdown fences.

OUTPUT SCHEMA:
{{"themes": [string, ...], "problems": [string, ...]}}
If nothing applies: {{"themes": ["Untagged"], "problems": ["Untagged"]}}
"""


@dataclass
class LLMTagResult:
    themes: list[str]
    problems: list[str]
    latency_ms: float
    cache_read_tokens: int = 0
    cache_creation_tokens: int = 0
    input_tokens: int = 0
    output_tokens: int = 0
    raw_response: str = ""
    error: str | None = None
    hallucinated: list[str] = field(default_factory=list)


class LLMTagger:
    def __init__(self, model: str = DEFAULT_MODEL, taxonomy_path: Path = TAXONOMY_PATH):
        self.model = model
        self.taxonomy = json.loads(taxonomy_path.read_text())
        self.system_prompt = _build_system_prompt(self.taxonomy)
        self.valid_themes = set(self.taxonomy["themes"]) | {"Untagged"}
        self.valid_problems = set(self.taxonomy["problems"].keys()) | {"Untagged"}
        self.client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

    def tag(self, title: str, text: str) -> LLMTagResult:
        user_msg = f"TITLE: {title}\nBODY: {text[:500]}\n\nClassify."
        t0 = time.perf_counter()
        try:
            resp = self.client.messages.create(
                model=self.model,
                max_tokens=300,
                temperature=0,
                system=[{
                    "type": "text",
                    "text": self.system_prompt,
                    "cache_control": {"type": "ephemeral"},
                }],
                messages=[{"role": "user", "content": user_msg}],
            )
        except Exception as e:
            return LLMTagResult(
                themes=["Untagged"], problems=["Untagged"],
                latency_ms=(time.perf_counter() - t0) * 1000,
                error=f"{type(e).__name__}: {e}",
            )

        latency_ms = (time.perf_counter() - t0) * 1000
        raw = resp.content[0].text if resp.content else ""

        themes, problems, hallucinated, parse_err = self._parse(raw)

        return LLMTagResult(
            themes=themes,
            problems=problems,
            latency_ms=latency_ms,
            cache_read_tokens=getattr(resp.usage, "cache_read_input_tokens", 0) or 0,
            cache_creation_tokens=getattr(resp.usage, "cache_creation_input_tokens", 0) or 0,
            input_tokens=resp.usage.input_tokens,
            output_tokens=resp.usage.output_tokens,
            raw_response=raw,
            error=parse_err,
            hallucinated=hallucinated,
        )

    def _parse(self, raw: str) -> tuple[list[str], list[str], list[str], str | None]:
        text = raw.strip()
        if text.startswith("```"):
            text = text.strip("`")
            if text.startswith("json"):
                text = text[4:]
            text = text.strip()
        try:
            obj = json.loads(text)
        except json.JSONDecodeError as e:
            return ["Untagged"], ["Untagged"], [], f"json_decode: {e}"

        themes_raw = obj.get("themes", []) or []
        problems_raw = obj.get("problems", []) or []
        if not isinstance(themes_raw, list) or not isinstance(problems_raw, list):
            return ["Untagged"], ["Untagged"], [], "non_list_fields"

        hallucinated = []
        themes = []
        for t in themes_raw:
            if t in self.valid_themes:
                if t not in themes:
                    themes.append(t)
            else:
                hallucinated.append(f"theme:{t}")
        problems = []
        for p in problems_raw:
            if p in self.valid_problems:
                if p not in problems:
                    problems.append(p)
            else:
                hallucinated.append(f"problem:{p}")

        if not themes:
            themes = ["Untagged"]
        if not problems:
            problems = ["Untagged"]
        return themes, problems, hallucinated, None
