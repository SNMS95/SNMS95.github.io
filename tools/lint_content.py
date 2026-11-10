#!/usr/bin/env python3
"""Lint the built site (dist/) for stale wording, private details and leaked drafts.

    npm run build && python3 tools/lint_content.py

Checks
  1. Stale wording: reuses STALE_PATTERNS from ../jobs/scripts/jobs.py (read with `ast`, so
     openpyxl is not needed). Skipped with a warning if that file is not there.
  2. Private details: the birth date and any e-mail address other than the public contact one,
     in HTML/XML and in cv.pdf. The exact values are read from ../jobs/profile/facts.md at
     runtime, never stored in this public repository.
  3. Drafts: no post with `draft: true` may appear in dist/.
  4. Empty links (href="") that would be dead buttons.

Run it locally before publishing; it is not part of CI because jobs/ lives outside this repo.
Standard library only. Exit code 1 if anything is found.
"""
from __future__ import annotations

import ast
import re
import shutil
import subprocess
import sys
from pathlib import Path

from _private import FULL_DATE, birth_year, dob_pattern, unexpected_emails

ROOT = Path(__file__).resolve().parent.parent
DIST = ROOT / "dist"
JOBS_PY = ROOT.parent / "jobs" / "scripts" / "jobs.py"
POSTS = ROOT / "src" / "content" / "posts"

# This repository is public: no personal value is written in this file. Exact private values
# (birth date, year) come from ../jobs/profile/facts.md via _private.py; the rest is generic.
# (regex, why), applied to every html/xml file in dist/ and to the text of cv.pdf.
def private_patterns() -> list[tuple[str, str]]:
    out = []
    dob = dob_pattern()
    if dob:
        out.append((dob, "birth date"))
    return out


# Only meaningful in the CV, where no other "Born" or birth year can legitimately occur.
def private_cv_only() -> list[tuple[str, str]]:
    out = [(r"\bBorn\b", "birth date line"), (FULL_DATE, "full date")]
    year = birth_year()
    if year:
        out.append((rf"\b{year}\b", "birth year"))
    return out


def load_stale_patterns() -> list[tuple[str, str]]:
    if not JOBS_PY.exists():
        print(f"warning: {JOBS_PY} not found; stale-wording check skipped.")
        return []
    tree = ast.parse(JOBS_PY.read_text(encoding="utf-8"))
    for node in tree.body:
        if isinstance(node, ast.Assign) and any(isinstance(t, ast.Name) and t.id == "STALE_PATTERNS" for t in node.targets):
            return [(str(p), str(advice)) for p, advice in ast.literal_eval(node.value)]
    print("warning: STALE_PATTERNS not found in jobs.py; stale-wording check skipped.")
    return []


def pdf_text(pdf: Path) -> str | None:
    if shutil.which("pdftotext"):
        out = subprocess.run(["pdftotext", str(pdf), "-"], capture_output=True, text=True)
        if out.returncode == 0:
            return out.stdout
    try:
        from pypdf import PdfReader  # type: ignore
    except ImportError:
        return None
    return "\n".join(page.extract_text() or "" for page in PdfReader(str(pdf)).pages)


def snippet(text: str, m: re.Match) -> str:
    a, b = max(m.start() - 30, 0), min(m.end() + 30, len(text))
    return re.sub(r"\s+", " ", text[a:b]).strip()


def draft_slugs() -> list[str]:
    slugs = []
    for f in sorted(POSTS.glob("*.md*")) if POSTS.exists() else []:
        head = f.read_text(encoding="utf-8").split("---", 2)
        if len(head) >= 3 and re.search(r"(?m)^draft:\s*true\s*$", head[1]):
            slugs.append(f.stem)
    return slugs


def main() -> int:
    if not DIST.exists():
        print("error: dist/ not found. Run `npm run build` first.")
        return 1

    problems: list[str] = []
    stale = load_stale_patterns()

    for f in sorted([*DIST.rglob("*.html"), *DIST.rglob("*.xml")]):
        rel = f.relative_to(DIST)
        text = f.read_text(encoding="utf-8", errors="replace")
        for pattern, advice in stale:
            for m in re.finditer(pattern, text):
                problems.append(f"{rel}: stale wording ({advice}): ...{snippet(text, m)}...")
        for pattern, why in private_patterns():
            for m in re.finditer(pattern, text):
                problems.append(f"{rel}: {why}: ...{snippet(text, m)}...")
        for email in unexpected_emails(text):
            problems.append(f"{rel}: unexpected e-mail address {email} (only the public contact address is allowed)")
        if re.search(r'href=""', text):
            problems.append(f"{rel}: empty href (a link with no URL is being rendered)")

    for slug in draft_slugs():
        hits = [str(p.relative_to(DIST)) for p in DIST.rglob("*") if slug in str(p.relative_to(DIST))]
        hits += [str(p.relative_to(DIST)) for p in [*DIST.rglob("*.html"), *DIST.rglob("*.xml")]
                 if f"/blog/{slug}" in p.read_text(encoding="utf-8", errors="replace")]
        if hits:
            problems.append(f"draft post '{slug}' leaked into dist/ ({', '.join(sorted(set(hits)))}); "
                            "rebuild without SHOW_DRAFTS")

    cv = DIST / "cv.pdf"
    if cv.exists():
        text = pdf_text(cv)
        if text is None:
            print("note: cv.pdf text not checked (install poppler or `pip install pypdf`); run `npm run cv` to rebuild it safely.")
        else:
            for pattern, why in [*private_patterns(), *private_cv_only(), *[(p, f"stale ({a})") for p, a in stale]]:
                for m in re.finditer(pattern, text):
                    problems.append(f"cv.pdf: {why}: ...{snippet(text, m)}...")
            for email in unexpected_emails(text):
                problems.append(f"cv.pdf: unexpected e-mail address {email}")
    else:
        print("note: no cv.pdf in dist/ (run `npm run cv`, then build again).")

    if problems:
        print(f"{len(problems)} problem(s):")
        for p in problems:
            print("  - " + p)
        return 1
    print("lint ok: no stale wording, private details, leaked drafts or empty links.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
