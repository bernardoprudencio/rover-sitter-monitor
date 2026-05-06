"""One-time migration: add `LLMTaggedAt` header column to both worksheets.

Writes:
  - "Reddit Posts"!I1         -> "LLMTaggedAt" (bold)
  - "Confluence Research"!M1  -> "LLMTaggedAt" (bold)

Idempotent: if the cell already contains "LLMTaggedAt", skip and report.
"""
from __future__ import annotations

import os

import gspread
from google.oauth2.service_account import Credentials

SHEET_ID = os.environ.get("SHEET_ID")
CREDS_FILE = os.environ.get("CREDS_FILE", "credentials.json")

HEADER_VALUE = "LLMTaggedAt"

TARGETS = [
    {"worksheet": "Reddit Posts", "cell": "I1"},
    {"worksheet": "Confluence Research", "cell": "M1"},
]


def _open_spreadsheet():
    if not SHEET_ID:
        raise SystemExit("FATAL: SHEET_ID env var not set. Source .env first.")
    if not os.path.exists(CREDS_FILE):
        raise SystemExit(f"FATAL: {CREDS_FILE} not found in {os.getcwd()}")
    scopes = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive",
    ]
    creds = Credentials.from_service_account_file(CREDS_FILE, scopes=scopes)
    client = gspread.authorize(creds)
    return client.open_by_key(SHEET_ID)


def _col_letter_to_index(letter: str) -> int:
    """A->1, B->2, ..., M->13."""
    n = 0
    for c in letter.upper():
        n = n * 26 + (ord(c) - ord("A") + 1)
    return n


def main() -> None:
    ss = _open_spreadsheet()
    for target in TARGETS:
        ws = ss.worksheet(target["worksheet"])
        cell = target["cell"]
        col_letter = "".join(c for c in cell if c.isalpha())
        needed_cols = _col_letter_to_index(col_letter)
        if ws.col_count < needed_cols:
            ws.add_cols(needed_cols - ws.col_count)
            print(f"[grid] {target['worksheet']}: expanded to {needed_cols} cols")
        existing = ws.acell(cell).value or ""
        if existing.strip() == HEADER_VALUE:
            print(f"[skip] {target['worksheet']}!{cell} already says '{HEADER_VALUE}'")
            continue
        if existing.strip():
            raise SystemExit(
                f"FATAL: {target['worksheet']}!{cell} is non-empty and not '{HEADER_VALUE}': "
                f"{existing!r}. Refusing to overwrite."
            )
        ws.update_acell(cell, HEADER_VALUE)
        ws.format(cell, {"textFormat": {"bold": True}})
        print(f"[wrote] {target['worksheet']}!{cell} = '{HEADER_VALUE}' (bold)")


if __name__ == "__main__":
    main()
