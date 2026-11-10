#!/usr/bin/env python3
"""Report GitHub activity that is not on the site yet. Read-only: it never edits anything.

    python3 tools/sync_github.py

Lists
  - repositories you merged pull requests into (not yours) that are not in
    `contributions` of src/data/software.yaml, and
  - your own public, non-fork repositories that are not in `projects`.
Entries in tools/sync_ignore.txt are skipped. You decide what goes on the site and edit the YAML.

Uses the public GitHub API. Set GITHUB_TOKEN (or log in with `gh`) for higher rate limits.
Standard library only.
"""
from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import sys
import urllib.error
import urllib.parse
import urllib.request
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
USER = "SNMS95"
SOFTWARE_YAML = ROOT / "src" / "data" / "software.yaml"
IGNORE_FILE = ROOT / "tools" / "sync_ignore.txt"
API = "https://api.github.com"


def token() -> str | None:
    if os.environ.get("GITHUB_TOKEN"):
        return os.environ["GITHUB_TOKEN"]
    if shutil.which("gh"):
        out = subprocess.run(["gh", "auth", "token"], capture_output=True, text=True)
        if out.returncode == 0 and out.stdout.strip():
            return out.stdout.strip()
    return None


def get(url: str, tok: str | None):
    headers = {"Accept": "application/vnd.github+json", "User-Agent": "github-contrib-sync"}
    if tok:
        headers["Authorization"] = f"Bearer {tok}"
    try:
        with urllib.request.urlopen(urllib.request.Request(url, headers=headers), timeout=30) as r:
            return json.load(r)
    except urllib.error.HTTPError as e:
        if e.code in (403, 429):
            raise SystemExit("error: GitHub rate limit hit. Wait a minute, or set GITHUB_TOKEN / run `gh auth login`.")
        raise SystemExit(f"error: GitHub API returned HTTP {e.code} for {url}")
    except urllib.error.URLError as e:
        raise SystemExit(f"error: could not reach GitHub ({e.reason}).")


def repo_keys(yaml_text: str, section: str) -> set[str]:
    """owner/repo (lowercase) for every github.com URL inside one top-level section of the YAML."""
    m = re.search(rf"(?ms)^{section}:\n(.*?)(?=^\S|\Z)", yaml_text)
    body = m.group(1) if m else ""
    return {f"{o}/{r}".lower() for o, r in re.findall(r"github\.com/([^/\s\"']+)/([^/\s\"']+)", body)}


def ignored() -> set[str]:
    if not IGNORE_FILE.exists():
        return set()
    lines = (re.sub(r"#.*", "", l).strip().lower() for l in IGNORE_FILE.read_text(encoding="utf-8").splitlines())
    return {l for l in lines if l}


def main() -> int:
    tok = token()
    yaml_text = SOFTWARE_YAML.read_text(encoding="utf-8")
    listed_contrib = repo_keys(yaml_text, "contributions")
    listed_projects = repo_keys(yaml_text, "projects")
    skip = ignored()

    # Merged PRs into other people's repositories.
    prs: dict[str, list[dict]] = defaultdict(list)
    q = urllib.parse.quote(f"author:{USER} is:pr is:merged -user:{USER}")
    for page in range(1, 6):
        data = get(f"{API}/search/issues?q={q}&per_page=100&page={page}", tok)
        for item in data.get("items", []):
            repo = item["repository_url"].split("/repos/")[1]
            prs[repo].append(item)
        if len(data.get("items", [])) < 100:
            break

    new_contrib = {r: v for r, v in prs.items() if r.lower() not in listed_contrib and r.lower() not in skip}

    # Own public, non-fork repositories.
    repos = get(f"{API}/users/{USER}/repos?per_page=100&sort=pushed&type=owner", tok)
    new_own = [r for r in repos if not r["fork"]
               and r["full_name"].lower() not in listed_projects and r["full_name"].lower() not in skip]

    if new_contrib:
        print("Merged PRs into repos that are not in `contributions` yet:")
        for repo, items in sorted(new_contrib.items(), key=lambda kv: -len(kv[1])):
            latest = max(i["closed_at"] for i in items)[:10]
            example = items[0]["title"]
            print(f"  {repo}  ({len(items)} PR{'s' if len(items) != 1 else ''}, latest {latest}), e.g. \"{example}\"")
    if new_own:
        print("Your public repos that are not in `projects` yet:")
        for r in new_own:
            print(f"  {r['full_name']}  (pushed {r['pushed_at'][:10]}): {r['description'] or 'no description'}")
    if not new_contrib and not new_own:
        print("Nothing new: every merged-PR repo and public repo is listed or in tools/sync_ignore.txt.")
    else:
        print("\nAdd what you want to src/data/software.yaml; add the rest to tools/sync_ignore.txt to silence them.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
