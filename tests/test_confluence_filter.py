"""Unit tests for the Confluence eligibility filter.

Rules + derivation: reviews/2026-05-05-confluence-filter-rules-derivation.md
"""
import pathlib
import sys
import types

# Stub gspread + google.oauth2 + requests + bs4 so we can import the module
# without the real network deps. We only exercise pure logic here.
for name, obj in {
    "gspread": types.SimpleNamespace(exceptions=types.SimpleNamespace(WorksheetNotFound=Exception)),
    "requests": types.SimpleNamespace(auth=types.SimpleNamespace(HTTPBasicAuth=object)),
    "bs4": types.SimpleNamespace(BeautifulSoup=object),
}.items():
    sys.modules.setdefault(name, obj)
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
_req_auth = types.ModuleType("requests.auth")
_req_auth.HTTPBasicAuth = object
sys.modules.setdefault("requests.auth", _req_auth)

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from rover_confluence_dump import evaluate_eligibility


# ── Doc-type whitelist hits ──────────────────────────────────────────────────

def test_findings_prefix_admits():
    ok, _ = evaluate_eligibility(
        "Findings: Groomer sign-up usability", "groomer onboarding feedback", [], "DSN"
    )
    assert ok


def test_early_findings_prefix_admits():
    ok, _ = evaluate_eligibility(
        "Early findings: New-to-Rover groomers", "groomer interviews", [], "DSN"
    )
    assert ok


def test_findings_report_prefix_admits():
    ok, _ = evaluate_eligibility(
        "Findings Report: Sitter Performance Score Interviews",
        "interviewed 12 sitters", [], "DSN"
    )
    assert ok


def test_findings_suffix_admits():
    """Suffix form: 'X: Findings'."""
    ok, _ = evaluate_eligibility(
        "Google Pay Checkout: Findings", "sitter checkout flow tests", [], "DSN"
    )
    assert ok


def test_writeup_suffix_admits():
    ok, _ = evaluate_eligibility(
        "Bookings on calendar: write Up", "sitter calendar usability", [], "DSN"
    )
    assert ok


def test_provider_survey_admits():
    """Sitter survey is a finding even without a 'findings' prefix."""
    ok, reason = evaluate_eligibility(
        "Sitter Non-response Survey - 2022, and 2026", "sitter responses", [], "DSN"
    )
    assert ok, reason


# ── Doc-type blacklist hits ──────────────────────────────────────────────────

def test_date_prefix_meeting_blocks():
    ok, reason = evaluate_eligibility(
        "2018-06-19 Decoupling on the Web Review", "agenda...", [], "DSN"
    )
    assert not ok
    assert reason.startswith("non_findings_title:")


def test_design_check_in_blocks():
    ok, reason = evaluate_eligibility(
        "2024-09-16 Design Check-in", "agenda", [], "DSN"
    )
    assert not ok
    assert reason.startswith("non_findings_title:")


def test_script_prefix_blocks():
    ok, reason = evaluate_eligibility(
        "Script: Training relationship page usability testing",
        "interview prompts about sitter training", [], "DSN"
    )
    assert not ok
    assert reason.startswith("non_findings_title:script")


def test_research_plan_blocks():
    ok, reason = evaluate_eligibility(
        "Research Plan: Cat in a Flat: Validating Assumptions", "sitter plan", [], "DSN"
    )
    assert not ok
    assert "research" in reason.lower() and "plan" in reason.lower()


def test_okr_timelines_block():
    ok, _ = evaluate_eligibility("Matteo Q2 2021 OKR Timelines", "", [], "DSN")
    assert not ok


def test_wip_marker_blocks():
    ok, _ = evaluate_eligibility(
        "Pet Sitting SEO City Page (WIP)", "sitter content", [], "DSN"
    )
    assert not ok


def test_meeting_notes_label_blocks():
    """Label blocklist trumps a positive title signal."""
    ok, reason = evaluate_eligibility(
        "Findings: Some random topic",  # title would normally admit
        "sitter feedback",
        ["meeting-notes"],
        "DSN",
    )
    assert not ok
    assert reason == "non_findings_label:meeting-notes"


# ── Audience filter ──────────────────────────────────────────────────────────

def test_psd_admits_by_default():
    """PSD = Provider Space; doc-type pass alone is sufficient."""
    ok, _ = evaluate_eligibility(
        "Findings: Rate ordering", "no provider terms in body", [], "PSD"
    )
    assert ok


def test_dsn_requires_provider_term_in_title():
    ok, _ = evaluate_eligibility(
        "Findings: Sitter onboarding flow", "", [], "DSN"
    )
    assert ok


def test_dsn_admits_on_body_provider_term():
    """No provider term in title — body should rescue."""
    ok, _ = evaluate_eligibility(
        "Findings: HVS early experiences",
        "Interviewed 8 sitters about home-visit signups.",
        [],
        "DSN",
    )
    assert ok


def test_dsn_rejects_when_no_provider_term():
    ok, reason = evaluate_eligibility(
        "Findings: Travel Time Distance",
        "Owners reviewed maps and chose ETAs.",
        [],
        "DSN",
    )
    assert not ok
    assert reason == "non_provider:dsn_no_provider_terms"


def test_dsn_seeker_only_rejected():
    """Seeker-only research with no provider mention should be excluded."""
    ok, reason = evaluate_eligibility(
        "Findings: Owner adoption survey",
        "We surveyed pet parents and adopters about adoption preferences.",
        [],
        "DSN",
    )
    assert not ok
    assert reason == "non_provider:dsn_no_provider_terms"


# ── Conflict cases ───────────────────────────────────────────────────────────

def test_blacklist_beats_whitelist():
    """Title that hits both lists — blacklist wins.

    Documented decision: the strictness bias is to exclude. A page titled
    'Script: Findings of pilot' is still a script (preparation doc).
    """
    ok, reason = evaluate_eligibility(
        "Script: Findings of pilot",
        "interview prompts for sitters",
        [],
        "DSN",
    )
    assert not ok
    assert reason.startswith("non_findings_title:script")


def test_no_findings_signal():
    """Plain title that's neither in the blacklist nor whitelist."""
    ok, reason = evaluate_eligibility(
        "Demographics Annual Survey",
        "We surveyed sitters about demographics.",
        [],
        "DSN",
    )
    assert not ok
    assert reason == "no_findings_signal"


def test_empty_inputs_safe():
    ok, reason = evaluate_eligibility("", "", [], "DSN")
    assert not ok
    assert reason == "no_findings_signal"


def test_reason_empty_when_eligible():
    ok, reason = evaluate_eligibility(
        "Findings: Sitter ratings", "sitter feedback", [], "DSN"
    )
    assert ok
    assert reason == ""


# ── Round 2 levers ───────────────────────────────────────────────────────────

def test_checklist_in_title_blocks():
    """Round 2 — Lever A. RACI checklists are planning, not findings."""
    ok, reason = evaluate_eligibility(
        "CSD sitter email survey checklist - Q4 2025",
        "Action item / Person and RACI role / Timing", [], "DSN"
    )
    assert not ok
    assert "checklist" in reason


def test_survey_request_blocks():
    """Round 2 — Lever A. 'Survey Request:' is a question-submission page."""
    ok, reason = evaluate_eligibility(
        "Sitter Survey Request: Promotion & Social Media",
        "We add questions pertaining to...", [], "DSN"
    )
    assert not ok


def test_bracket_draft_blocks():
    """Round 2 — Lever B. [draft] should block alongside (draft)."""
    ok, _ = evaluate_eligibility(
        "Groomer pricing survey [draft]", "Status Planning", [], "DSN"
    )
    assert not ok


def test_acceleration_findings_admits():
    """Round 2 — Lever D. 'Acceleration #N:' is internal Rover findings lingo."""
    ok, _ = evaluate_eligibility(
        "Acceleration #3: Sitter self-promotion and sharing behaviors",
        "Executive Summary: Sitters were active on social media platforms...",
        [],
        "DSN",
    )
    assert ok
