# snms95.github.io

Personal site of Surya Manoj Sanu: papers, software and short notes. Built with [Astro](https://astro.build) (static output, plain CSS), deployed to GitHub Pages by GitHub Actions. Live at https://snms95.github.io.

```sh
npm install
npm run dev        # preview at http://localhost:4321 while you edit
npm run verify     # type check + production build + content lint
```

Needs Node 22+ (24 recommended). The CV and lint tools also need Python 3 and `latexmk`.

## Cheat sheet: what do you want to change?

| I want to ... | Edit | Details |
| --- | --- | --- |
| change the intro text, role line or header links | `src/data/profile.yaml` | [Change existing details](#change-existing-details) |
| add or fix a paper (DOI, arXiv, PDF, code, BibTeX) | `src/data/papers.yaml` | [Papers](#papers) |
| add a project, or a repo I contributed to | `src/data/software.yaml` | [Software](#software-and-contributions) |
| add a talk | `src/data/talks.yaml` | [Talks](#talks) |
| write or unpublish a blog post | `src/content/posts/<slug>.md` | [Blog posts](#blog-posts) |
| add a whole new section to the front page | new YAML + 3 small edits | [New section](#add-a-new-section-to-the-front-page) |
| add a new page such as `/teaching/` | `src/pages/<name>.astro` | [New page](#add-a-new-page) |
| update the CV | the CV source in `../jobs`, then `npm run cv` | [CV](#update-the-cv) |
| change colours, fonts, nav labels, page title | `global.css`, `Base.astro`, `index.astro` | [Look and wording](#change-the-look-and-the-wording) |
| replace the logo | `src/assets/motif.svg`, `public/favicon.svg` | [Logo](#replace-the-logo) |

Every change follows the same loop, described in [Preview, check, publish](#preview-check-publish).

## Change existing details

All page content lives in `src/data/*.yaml`; the components only lay it out. Edit the YAML, never the generated pages.

**`profile.yaml`**

| Key | Meaning |
| --- | --- |
| `name` | page heading and header text |
| `role`, `location` | the small line under the name |
| `intro` | list of paragraphs; add or remove list items freely |
| `links` | `label` + `url` pairs shown under the intro (`/cv.pdf` is the CV) |

**Order is file order.** To reorder papers, projects, links or talks, move the block up or down. To remove an entry, delete its block.

**YAML pitfalls.** Indent with spaces, never tabs. Put a value in quotes when it contains a colon or `#` or starts with a special character (`title: "Neural topology optimization: the good, the bad"`). A build that fails with a YAML error is almost always one of these.

## Papers

Add a block to `src/data/papers.yaml`, newest first:

```yaml
- id: my-paper            # short unique id, used as the anchor (/#my-paper)
  title: Title of the paper
  authors: S. M. Sanu and A. N. Other
  venue: Journal Name 12, 345
  year: 2026
  doi: 10.1234/abcd       # the bare DOI, not a URL
  arxiv: 2601.01234       # an arXiv id or a full URL
  pdf: ""                 # a full URL
  code: ""                # a full URL
  codeNote: ""            # one line of plain text under the venue, e.g. "Code release coming soon"
  bibtex: |-              # optional; adds a BibTeX button that copies it
    @article{key,
      title = {Title of the paper},
      ...
    }
```

An empty field hides its button, so a paper can go up before its links exist. Buttons appear in the order DOI, arXiv, PDF, Code, BibTeX.

## Software and contributions

`src/data/software.yaml` has two lists:

```yaml
projects:                 # your own work, shown with a description
  - name: MyTool
    url: https://github.com/SNMS95/MyTool   # leave "" for something unreleased: it is shown as plain text
    status: ""            # optional small tag, e.g. "Open-source release coming soon"
    blurb: One or two plain sentences about what it does.

contributions:            # other people's projects, shown as a one-line list of names
  - name: SomeProject
    url: https://github.com/owner/SomeProject
```

`npm run sync-github` lists repositories you merged pull requests into, and public repos of yours, that are not on the page yet. It edits nothing. Anything you decide not to list can be silenced in `tools/sync_ignore.txt`.

## Talks

`src/data/talks.yaml`:

```yaml
- name: WCSMO                                  # short name shown on the page
  full: World Congress of Structural and Multidisciplinary Optimization   # tooltip on hover
  years: 2023, 2025
```

## Blog posts

Create `src/content/posts/<slug>.md`. The file name becomes the address: `my-first-post.md` is served at `/blog/my-first-post/`.

```md
---
title: "What I learned about implicit differentiation"
date: 2026-12-01          # YYYY-MM-DD
summary: "One sentence for the post list and the RSS feed."
tags: ["jax", "autodiff"] # optional
draft: false              # true keeps it out of the published site
---

Write in Markdown. Inline math $x^2$ and display math $$\int_0^1 f(x)\,dx$$ work,
as do fenced code blocks with a language, footnotes[^1], tables and links.

[^1]: Like this.
```

- **Where posts show up:** the 5 newest on the front page (in a "Writing" section), all of them on `/blog/`, and in the RSS feed at `/rss.xml`. The "Writing" section and nav link appear as soon as the first non-draft post exists.
- **Images:** put the file in `public/images/` and reference it as `![Alt text](/images/figure.png)`. Always write alt text.
- **Draft first:** start with `draft: true`, preview with `SHOW_DRAFTS=1 npm run dev`, then change it to `false` and publish. Drafts are never built, so they cannot leak.
- **Unpublish:** set `draft: true` (keeps the file) or delete the file, then publish.
- **Edit later:** change the file and publish. Do not rename a published file: that changes its address and breaks links to it.
- `example-math-code.md` is a draft that exists only to test rendering. Copy it as a starting point or delete it.

## Add a new section to the front page

Example: a "News" section. It takes one data file and three small edits.

1. Create `src/data/news.yaml`:

   ```yaml
   - when: "2026-12"
     text: One line of news.
   ```

2. In `src/lib/data.ts`, add the import, the type and the export next to the existing ones:

   ```ts
   import newsRaw from '../data/news.yaml?raw';

   export interface NewsItem {
     when: string;
     text: string;
   }

   export const news = load(newsRaw) as NewsItem[];
   ```

3. In `src/pages/index.astro`, add `news` to the import from `'../lib/data'`, then add the section where you want it to appear (sections show in file order):

   ```astro
   <section id="news" aria-labelledby="news-h">
     <h2 class="label" id="news-h">News</h2>
     <ul class="posts">
       {news.map((n) => <li><time>{n.when}</time> {n.text}</li>)}
     </ul>
   </section>
   ```

4. Optional: add a nav link in `src/layouts/Base.astro`, inside the `<ul>` in the header: `<li><a href="/#news">News</a></li>`.

The classes `label` (section heading), `posts` (dated list) and `inline-list` (dot-separated list) are defined in `src/styles/global.css`; reuse them to stay consistent. To hide or remove a section, delete its `<section>` block in `index.astro`.

## Add a new page

Create `src/pages/teaching.astro`; it is served at `/teaching/` and added to the sitemap automatically:

```astro
---
import Base from '../layouts/Base.astro';
---

<Base title="Teaching · Surya Manoj Sanu" description="One sentence for search engines and link previews.">
  <h1>Teaching</h1>
  <p class="role">One line that says what this page is.</p>
  <p>Your text here.</p>
</Base>
```

Link to it from `Base.astro` (`<li><a href="/teaching/">Teaching</a></li>`) or from any other page.

## Update the CV

The public CV is built from the research CV template, `../jobs/templates/cv_research.tex`, which stays the single source of truth. Never edit `public/cv.pdf` by hand.

1. Change the CV in `../jobs` (and its facts file first, following the rules of that project).
2. Run `npm run cv`. The script copies the template to a temporary folder, removes the birth date, refuses to continue if anything private is left or referees are switched on, compiles it with `latexmk`, requires at most 2 pages, and writes `public/cv.pdf`.
3. Publish as usual; commit `public/cv.pdf` together with any other changes.

Notes:

- The PDF is built on your computer, not in CI (the CV source is outside this repository), and it cannot be updated from GitHub's web editor.
- For the strongest safety net install a PDF text reader once (`brew install poppler`, or `pip install pypdf`). With it, `npm run cv` also checks the finished PDF's text, not just the source.
- The link and its label are in `src/data/profile.yaml` (`/cv.pdf`).

## Change the look and the wording

| What | Where |
| --- | --- |
| colours (background, text, accent, rules), light and dark | the tokens at the top of `src/styles/global.css`; each is `light-dark(light value, dark value)` |
| fonts | `--serif` and `--mono` in `global.css`; self-hosted through Fontsource, so install the package (`npm i @fontsource-variable/<font>`) and import it in `Base.astro` |
| text column width | `--measure` in `global.css` |
| nav labels and order | the `<nav>` list in `src/layouts/Base.astro` |
| browser tab title and search description of the front page | `description` in `src/pages/index.astro` (the title is `name` from `profile.yaml`) |
| footer | the `<footer>` in `Base.astro`; "Last updated" is the build date and updates itself |

## Replace the logo

The arch in the header is a placeholder.

- `src/assets/motif.svg` is the header mark. It is inlined and coloured by the accent through `currentColor`, so keep strokes and fills on `currentColor`.
- `public/favicon.svg` is the browser-tab icon. It has its own colours and a dark-mode rule.
- For link previews (LinkedIn, Slack), add a 1200x630 `public/og.png` and an `og:image` meta tag in `src/layouts/Base.astro`.

## Preview, check, publish

```sh
npm run dev                 # 1. preview while you edit
npm run verify              # 2. type check, production build, content lint
git add -A
git commit -m "Describe the change"
git push                    # 3. GitHub Actions builds and deploys, about a minute
```

Check the result in the repository's Actions tab, or with `gh run list` / `gh run watch`. If a run fails, `gh run view --log-failed` shows why.

- **Small text edits** (YAML or Markdown) can also be made in the browser on github.com with the pencil icon; committing to `main` deploys automatically. That skips `npm run verify`, so double-check the page afterwards. It does not work for the CV.
- **Roll back** a bad change with `git revert <commit>` and push. The previous version is rebuilt.
- **The site did not change after a push:** look at the Actions tab for a failed run, hard-refresh the browser, and make sure Settings > Pages uses the source "GitHub Actions".
- **A link button is missing:** that field is empty or misspelled in the YAML.

`npm run verify` runs `tools/lint_content.py` on the built site: stale wording (it reuses `STALE_PATTERNS` from `../jobs/scripts/jobs.py`), the birth date, any e-mail address other than the public contact one, leaked drafts and empty links.

**This repository is public. Never put private details in any file here, not even in a comment or a script.** The birth date and similar values are read from `../jobs/profile/facts.md` at run time by `tools/_private.py`, so they never enter the repository.

## How it is built

Pushing to `main` runs `.github/workflows/deploy.yml`, which builds the site and deploys it to GitHub Pages. The repository must stay named `SNMS95.github.io` for the site to be served at `https://snms95.github.io`.

```
src/data/        YAML content (edit these)
src/content/     blog posts (Markdown)
src/components/  Paper, Project, PostList, Motif
src/layouts/     Base.astro: head, header, footer, theme toggle, BibTeX copy
src/lib/         data.ts (typed loaders for the YAML), posts.ts (draft handling)
src/pages/       index, blog/, rss.xml, 404
src/styles/      global.css (tokens, light/dark, typography)
public/          files served as they are: cv.pdf, favicon.svg, images/
tools/           build_cv.py, lint_content.py, sync_github.py, _private.py, sync_ignore.txt
```

Fonts (Source Serif 4, JetBrains Mono) are self-hosted through Fontsource. No analytics, no cookies, no third-party requests.
