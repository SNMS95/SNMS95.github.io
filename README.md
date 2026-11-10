# snms95.github.io

Personal site of Surya Manoj Sanu: papers, software and short notes. Built with [Astro](https://astro.build) (static output, plain CSS), deployed to GitHub Pages by GitHub Actions.

```sh
npm install
npm run dev        # http://localhost:4321
npm run verify     # type check + production build + content lint
```

Needs Node 22+ (24 recommended) and, for the CV and lint tools, Python 3 and `latexmk`.

## Everyday tasks

**Add or change a paper, project, talk or contribution.** Edit the YAML in `src/data/`. An empty link hides its button, so a paper can go up before its arXiv link exists. Fill in `doi`, `arxiv`, `pdf`, `code` and `bibtex` when you have them.

| File | Holds |
| --- | --- |
| `src/data/profile.yaml` | name, role, intro text, header links |
| `src/data/papers.yaml` | publications (newest first) |
| `src/data/software.yaml` | `projects` (your own) and `contributions` (other people's repos, name only) |
| `src/data/talks.yaml` | conference talks |

**Write a post.** Add `src/content/posts/<slug>.md`:

```md
---
title: "What I learned about ..."
date: 2026-12-01
summary: "One sentence for the list and the RSS feed."
tags: ["jax"]
draft: false
---
```

Math (`$...$`, `$$...$$`), code fences, footnotes, tables and images work. `draft: true` keeps a post out of the build. To preview drafts, run `SHOW_DRAFTS=1 npm run dev`. The "Writing" section and nav link appear once the first non-draft post exists.

**Update the CV.** The CV source of truth is `../jobs/templates/cv_research.tex`. Run `npm run cv`: it copies the template, removes the birth date, refuses to continue if anything private is left, compiles with `latexmk` (at most 2 pages) and writes `public/cv.pdf`. Commit the new PDF.

**Check what is missing from the site.** `npm run sync-github` lists repos you merged PRs into, and public repos of yours, that are not on the page yet. It edits nothing. Silence entries in `tools/sync_ignore.txt`.

**Before publishing.** `npm run verify` and make sure `cv.pdf` is current. The lint checks the built site for stale wording (it reuses `STALE_PATTERNS` from `../jobs/scripts/jobs.py`), the birth date, referee emails, leaked drafts and empty links.

## Replacing the logo

The arch in the header is a placeholder.

- `src/assets/motif.svg` is the header mark. It is inlined and coloured by the accent through `currentColor`, so keep strokes and fills on `currentColor`.
- `public/favicon.svg` is the browser-tab icon. It has its own colours and a dark-mode rule.
- For link previews (LinkedIn, Slack), add a 1200x630 `public/og.png` and an `og:image` meta tag in `src/layouts/Base.astro`.

## Publishing

Pushing to `main` runs `.github/workflows/deploy.yml`, which builds the site and deploys it to GitHub Pages. In the repository settings, Pages must use the source "GitHub Actions". The repository has to be named `SNMS95.github.io` for the site to be served at `https://snms95.github.io`.

`cv.pdf` is committed, not built in CI, because the CV source lives outside this repository.

## Layout

```
src/data/        YAML content (edit these)
src/content/     blog posts (Markdown)
src/components/  Paper, Project, PostList, Motif
src/layouts/     Base.astro: head, header, footer, theme toggle, BibTeX copy
src/pages/       index, blog/, rss.xml, 404
src/styles/      global.css (tokens, light/dark, typography)
tools/           build_cv.py, lint_content.py, sync_github.py
```

Fonts (Source Serif 4, JetBrains Mono) are self-hosted through Fontsource. No analytics, no cookies, no third-party requests.
