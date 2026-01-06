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

**After ANY change to data, templates, or CSS, re-run the generator** to keep HTML files in sync.

## Architecture

Single-script static site generator following an MVC-like pattern:

- **Data layer** (`data/`): YAML, BibTeX, and Markdown source files
- **View layer** (`templates/`): Jinja2 HTML templates with `layout.html` as base
- **Controller** (`generate_site.py`): Parses data, renders templates, writes HTML to repo root

**Data flow:** BibTeX/YAML/MD → parse functions → Jinja2 rendering → HTML output

### Key files

| File | Purpose |
|------|---------|
| `data/vita.bib` | Publications in BibTeX; `@unpublished` entries appear in projects, not publications |
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
- `render_markdown()` with minimal subset support (H1-H3, links, paragraphs)
- Publication filtering by keywords: `peer_reviewed`, `technical_report`, `open_source`, `essay`

Generated pages: `index.html`, `publications.html`, `projects.html`, `teaching.html`, `future-politics.html`

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
