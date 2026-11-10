"""Private values the public site must never show, read at runtime from ../jobs/profile/facts.md.

This repository is public, so the birth date and referee addresses are deliberately NOT written
anywhere in it, not even as patterns. The tools combine generic rules (a "Born" line, a full
dd/mm/yyyy date, any e-mail address other than the public contact address) with the exact values
found in facts.md when that file is available.
"""
from __future__ import annotations

import re
from pathlib import Path

FACTS = Path(__file__).resolve().parent.parent.parent / "jobs" / "profile" / "facts.md"
CONTACT_EMAIL = "sm95sanu@gmail.com"  # shown on the site on purpose
EMAIL_RE = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9-]+(?:\.[A-Za-z0-9-]+)+")
FULL_DATE = r"\b\d{1,2}/\d{1,2}/\d{4}\b"
MONTHS = ["January", "February", "March", "April", "May", "June", "July", "August",
          "September", "October", "November", "December"]


def _birth() -> tuple[int, int, int] | None:
    if not FACTS.exists():
        return None
    m = re.search(r"Born:?\**\s*(\d{1,2})/(\d{1,2})/(\d{4})", FACTS.read_text(encoding="utf-8"))
    return (int(m[1]), int(m[2]), int(m[3])) if m else None


def dob_pattern() -> str | None:
    """Regex for the birth date in common written forms, or None if facts.md has no date."""
    b = _birth()
    if not b:
        return None
    d, mo, y = b
    month = MONTHS[mo - 1]
    forms = [f"{d:02d}/{mo:02d}/{y}", f"{d}/{mo}/{y}", f"{y}-{mo:02d}-{d:02d}", f"{d:02d}.{mo:02d}.{y}",
             f"{d} {month} {y}", f"{d:02d} {month} {y}", f"{month} {d}, {y}"]
    return "|".join(re.escape(f) for f in dict.fromkeys(forms))


def birth_year() -> str | None:
    b = _birth()
    return str(b[2]) if b else None


def unexpected_emails(text: str) -> list[str]:
    """E-mail addresses in `text` other than the public contact address."""
    return sorted({m.group(0) for m in EMAIL_RE.finditer(text) if m.group(0).lower() != CONTACT_EMAIL})
