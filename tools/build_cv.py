#!/usr/bin/env python3
"""Build public/cv.pdf from the research CV template in ../jobs, without private details.

The template is the single source of truth for the CV. This script copies it to a temporary
folder, removes the birth date, refuses to continue if anything private is left, compiles it
with latexmk (same flags as jobs/scripts/jobs.py:compile_tex) and copies the PDF to public/.

    python3 tools/build_cv.py [--source PATH] [--out PATH]

Standard library only. Exit code 1 on any problem.
"""
from __future__ import annotations

import argparse
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

from _private import FULL_DATE, birth_year, dob_pattern, unexpected_emails

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_SOURCE = ROOT.parent / "jobs" / "templates" / "cv_research.tex"
DEFAULT_OUT = ROOT / "public" / "cv.pdf"

# Each pattern must match exactly once. If it does not, the template has drifted and a human
# should look before anything is published.
REMOVALS = [
    ("birth date", r"Born \d{1,2}/\d{1,2}/\d{4} \\enspace\$\\cdot\$\\enspace "),
]

# Must not appear in the TeX source (comments excluded) after the removals. This repository is
# public, so no personal value is written here; exact private values come from _private.py.
SOURCE_FORBIDDEN = [
    (r"\bBorn\b", "birth date line"),
    (FULL_DATE, "full date"),
    (r"\\showrefstrue", "referees switched on"),
    (r"\\todo\{", "unfinished placeholder"),
]

MAX_PAGES = 2


def strip_tex_comments(text: str) -> str:
    return "\n".join(re.sub(r"(?<!\\)%.*", "", line) for line in text.splitlines())


def sanitize(tex: str) -> str:
    for what, pattern in REMOVALS:
        tex, n = re.subn(pattern, "", tex)
        if n != 1:
            raise SystemExit(f"error: expected to remove the {what} exactly once, matched {n} times. "
                             "The template changed; update REMOVALS in tools/build_cv.py.")
    if not re.search(r"^\s*\\showrefsfalse", strip_tex_comments(tex), re.MULTILINE):
        raise SystemExit("error: \\showrefsfalse not found; referees must stay off on the public CV.")
    visible = strip_tex_comments(tex)
    for pattern, why in SOURCE_FORBIDDEN:
        if re.search(pattern, visible):
            raise SystemExit(f"error: {why} still in the CV source (pattern {pattern!r}).")
    dob = dob_pattern()
    if dob and re.search(dob, visible):
        raise SystemExit("error: the birth date (from facts.md) is still in the CV source.")
    # Best-effort PDF metadata; skipped silently if the marker line is not there.
    meta = r"\hypersetup{pdftitle={Surya Manoj Sanu: CV}, pdfauthor={Surya Manoj Sanu}}"
    return tex.replace(r"\pagenumbering{gobble}", meta + "\n" + r"\pagenumbering{gobble}", 1)


def compile_pdf(workdir: Path) -> int | None:
    if shutil.which("latexmk") is None:
        raise SystemExit("error: latexmk not found; install MacTeX / TeX Live.")
    cmd = ["latexmk", "-pdf", "-interaction=nonstopmode", "-halt-on-error", "-quiet", "cv.tex"]
    try:
        proc = subprocess.run(cmd, cwd=workdir, capture_output=True, text=True, timeout=240)
    except subprocess.TimeoutExpired:
        raise SystemExit("error: LaTeX timed out.")
    log_file = workdir / "cv.log"
    log = log_file.read_text(errors="replace") if log_file.exists() else proc.stdout + proc.stderr
    if proc.returncode != 0:
        errors = [line for line in log.splitlines() if line.startswith("!")][:3]
        raise SystemExit(f"error: LaTeX failed ({'; '.join(errors) or 'see cv.log'}).")
    m = re.search(r"Output written on .*?\((\d+) pages?", log.replace("\n", ""))
    return int(m.group(1)) if m else None


def pdf_text(pdf: Path) -> str | None:
    """Text of the PDF via poppler or pypdf, whichever is installed; None if neither."""
    if shutil.which("pdftotext"):
        out = subprocess.run(["pdftotext", str(pdf), "-"], capture_output=True, text=True)
        if out.returncode == 0:
            return out.stdout
    try:
        from pypdf import PdfReader  # type: ignore
    except ImportError:
        return None
    return "\n".join(page.extract_text() or "" for page in PdfReader(str(pdf)).pages)


def pdf_leaks(text: str) -> list[str]:
    """What is wrong with the PDF text, as short descriptions (empty list = clean)."""
    found = []
    for pattern, why in [(r"\bBorn\b", "birth date line"), (FULL_DATE, "full date")]:
        if re.search(pattern, text):
            found.append(why)
    dob, year = dob_pattern(), birth_year()
    if dob and re.search(dob, text):
        found.append("birth date")
    if year and re.search(rf"\b{year}\b", text):
        found.append("birth year")
    emails = unexpected_emails(text)
    if emails:
        found.append(f"unexpected e-mail address ({', '.join(emails)})")
    return found


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--source", type=Path, default=DEFAULT_SOURCE, help="CV template (default: ../jobs/templates/cv_research.tex)")
    ap.add_argument("--out", type=Path, default=DEFAULT_OUT, help="output PDF (default: public/cv.pdf)")
    args = ap.parse_args()

    if not args.source.exists():
        raise SystemExit(f"error: {args.source} not found.")
    tex = sanitize(args.source.read_text(encoding="utf-8"))

    with tempfile.TemporaryDirectory(prefix="cv-build-") as tmp:
        work = Path(tmp)
        (work / "cv.tex").write_text(tex, encoding="utf-8")
        pages = compile_pdf(work)
        if pages is None or pages > MAX_PAGES:
            raise SystemExit(f"error: CV is {pages} pages; the limit is {MAX_PAGES}.")
        built = work / "cv.pdf"

        text = pdf_text(built)
        if text is None:
            print("note: PDF text not checked (install poppler or `pip install pypdf` to enable); "
                  "the TeX source was checked.")
        else:
            leaks = pdf_leaks(text)
            if leaks:
                raise SystemExit(f"error: the built PDF contains: {'; '.join(leaks)}. Nothing written.")

        args.out.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(built, args.out)

    print(f"ok: {args.out.relative_to(ROOT) if args.out.is_relative_to(ROOT) else args.out} "
          f"({pages} pages, {args.out.stat().st_size // 1024} KB) from {args.source}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
