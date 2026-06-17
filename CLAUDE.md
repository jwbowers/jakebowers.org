# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Static academic website for Jake Bowers (jakebowers.org), generated locally using Python and deployed to GitHub Pages. The `main` branch contains source data, templates, CSS, and the generator script. The `gh-pages` branch contains only generated HTML.

## Build Commands

**Local development (recommended):**
```bash
uv run python generate_site.py
```

**Alternative (requires manual dependency installation):**
```bash
python generate_site.py
```

Requires Python 3.14+ with `jinja2` and `pyyaml` dependencies.

**The generated HTML pages are git-ignored, not tracked.** CI rebuilds them from `data/` + `templates/` on every push to `main` (see `.github/workflows/build.yml`) and deploys the result to `gh-pages`, so the files under `data/`, `templates/`, and `static/` are the single source of truth. Run the generator locally only to preview changes in a browser; the resulting HTML stays on disk but is not committed.

## Bibliography source

`data/vita.bib` is **not** the source of truth. The canonical bibliography lives
in a separate private repo at `~/repos/vita/vita.bib` (`github.com:jwbowers/vita`),
where new entries are normally added. The copy here is a derived mirror.

Because the vita repo is private, CI cannot fetch it at build time, so the mirror
is committed to this repo and refreshed by hand with `bin/sync-vita-bib.sh`:

- Run with no arguments to **check** (read-only) whether the mirror matches the
  canonical. Exit 0 if in sync, 1 if diverged.
- Run with `--apply` to copy canonical -> mirror. It refuses if the mirror has
  lines absent from the canonical (a sign of a direct edit that should be ported
  upstream first); `--apply --force` overrides after you confirm those lines are
  stale.

Do not hand-edit `data/vita.bib`. Edit `~/repos/vita/vita.bib`, then sync. If you
ever do fix something in the mirror, port it back to the canonical and re-sync.

## Architecture

Single-script static site generator following an MVC-like pattern:

- **Data layer** (`data/`): YAML, BibTeX, and Markdown source files
- **View layer** (`templates/`): Jinja2 HTML templates with `layout.html` as base
- **Controller** (`generate_site.py`): Parses data, renders templates, writes HTML to repo root

**Data flow:** BibTeX/YAML/MD → parse functions → Jinja2 rendering → HTML output

### Key files

| File | Purpose |
|------|---------|
| `data/vita.bib` | Publications in BibTeX, a derived mirror of the canonical `~/repos/vita/vita.bib` (see Bibliography source below); `@unpublished` entries appear in projects, not publications |
| `data/projects.yaml` | Current projects, backburner projects, software |
| `data/teaching.yaml` | Courses and syllabus links |
| `data/bio.md` | Front-page biography (limited Markdown: headings, links, paragraphs) |
| `data/config.yaml` | Site name, author name, vita PDF path |
| `templates/layout.html` | Base template (header, nav, footer) |
| `static/css/style.css` | Single global stylesheet |

### Generator internals

`generate_site.py` includes:
- Custom BibTeX parser (no external library) — handles nested braces
- `safe_year()` helper for parsing BibTeX years like `{2006}` — **do not remove**
- `render_markdown()` with minimal subset support (H1-H3, links, paragraphs, bulleted lists with `- `)
- Publication filtering by keywords: `peer_reviewed`, `technical_report`, `open_source`, `essay`

Generated pages (written to the repo root, git-ignored, rebuilt by CI on deploy): `index.html`, `publications.html`, `projects.html`, `teaching.html`, `future-politics.html`

## Static File Hosting (AWS S3)

PDFs and other static files (syllabi, vita, etc.) are served from the S3 bucket `static.jakebowers.org`, accessible at `https://static.jakebowers.org/`. The site templates link to these URLs directly (not to files in this repo).

**Uploading files — always include `--acl public-read`:**
```bash
aws s3 cp <local-file> s3://static.jakebowers.org/MISC/<filename> --acl public-read
```

For example, to update the vita:
```bash
aws s3 cp ~/repos/vita/bowers-vita.pdf s3://static.jakebowers.org/MISC/bowers-vita.pdf --acl public-read
```

The bucket has no bucket policy — public access is controlled per-object via ACLs. **Without `--acl public-read`, uploaded files will be private and return 403 Forbidden errors.**

Note: `data/config.yaml` has a `vita_pdf` field, but it is not currently used by the templates. The S3 URL is hardcoded in `templates/layout.html` and `templates/index.html`.

## Testing

No automated test suite. Manual verification:
1. Run `python generate_site.py`
2. Open generated HTML files in browser
3. Verify layout, links, and content

## Style Guidelines

- **Python:** 4-space indentation
- **YAML:** 2-space indentation; use block scalars (`|`) for multi-line descriptions
- **Templates:** Standard HTML with Jinja2 delimiters; keep markup minimal to match existing style
- **Commits:** Short, sentence-style messages describing user-facing changes
