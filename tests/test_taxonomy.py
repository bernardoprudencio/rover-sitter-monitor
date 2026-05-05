"""Smoke tests for taxonomy.json + rover_sheet_dump.tag_post regression."""
import json
import pathlib
import sys
import types

# Stub gspread + google.oauth2 so we can import rover_sheet_dump without the real deps.
# The test only exercises tag_post / PROBLEMS / PROBLEM_TO_THEME, not sheet I/O.
_g = types.ModuleType("gspread")
_g.exceptions = types.SimpleNamespace(WorksheetNotFound=Exception)
sys.modules.setdefault("gspread", _g)
_google = types.ModuleType("google")
_oauth2 = types.ModuleType("google.oauth2")
_sa = types.ModuleType("google.oauth2.service_account")
_sa.Credentials = type("Credentials", (), {
    "from_service_account_info": staticmethod(lambda *a, **k: None),
    "from_service_account_file": staticmethod(lambda *a, **k: None),
})
sys.modules.setdefault("google", _google)
sys.modules.setdefault("google.oauth2", _oauth2)
sys.modules.setdefault("google.oauth2.service_account", _sa)

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from rover_sheet_dump import PROBLEMS, PROBLEM_TO_THEME, tag_post


def test_taxonomy_loads_and_is_consistent():
    tax = json.loads((ROOT / "taxonomy.json").read_text())
    assert tax["schema_version"] == 1
    declared = set(tax["themes"])
    assert len(declared) == 13
    assert len(tax["problems"]) == 107
    for problem, meta in tax["problems"].items():
        assert meta["theme"] in declared, f"{problem!r} → unknown theme {meta['theme']!r}"
        assert isinstance(meta["keywords"], list) and meta["keywords"], f"{problem!r} has no keywords"
    assert set(PROBLEM_TO_THEME) == set(tax["problems"])
    assert set(PROBLEMS) == set(tax["problems"])


def test_tag_post_known_samples():
    """Locked baseline — must not change after the JSON refactor."""
    themes, problems = tag_post("Anyone got tips for a new puppy?", "")
    assert themes == ["Preferences and rates"]
    assert problems == ["Puppies"]

    themes, problems = tag_post("how to track miles for taxes", "")
    assert "Taxes" in themes
    assert "Track mileage" in problems

    themes, problems = tag_post("GPS is wrong on rover card again", "tracking is off")
    assert "Rover Cards" in themes
    assert "GPS accuracy" in problems

    themes, problems = tag_post("just saying hi", "")
    assert themes == ["Untagged"]
    assert problems == ["Untagged"]


def test_tag_post_multi_match():
    """A post can match multiple problems; themes deduped, problems all kept."""
    themes, problems = tag_post("My puppy is a senior dog now", "")
    assert "Puppies" in problems
    assert "Senior dogs" in problems
    assert themes.count("Preferences and rates") == 1  # deduped
