# Repository Guidelines

## Project Structure & Module Organization
- `generate_site.py` renders the static site from data and templates.
- `data/` holds content sources: `bio.md`, `vita.bib`, `projects.yaml`, `teaching.yaml`, and `config.yaml`.
- `templates/` contains Jinja2 HTML templates (`layout.html` plus page templates).
- `static/css/style.css` is the global stylesheet.
- Generated pages live in the repo root: `index.html`, `publications.html`, `projects.html`, `teaching.html`.

## Build, Test, and Development Commands
- `python generate_site.py` regenerates all HTML pages from `data/` + `templates/`.
  - Requires Python 3 with `jinja2` and `PyYAML` installed.
- There is no build system beyond the generator; open the HTML files locally to verify changes.

## Coding Style & Naming Conventions
- Python: 4-space indentation, keep helpers like `safe_year()` intact (used for BibTeX year parsing).
- YAML: 2-space indentation; use block scalars (`|`) for multi-line descriptions.
- Templates: standard HTML with Jinja2 delimiters (`{{ }}`, `{% %}`); keep markup minimal to match existing style.

## Testing Guidelines
- No automated test suite is present.
- Manual checks: run `python generate_site.py`, then open the generated HTML pages to confirm layout, links, and content.
- If you add tests, keep them lightweight and document how to run them.

## Commit & Pull Request Guidelines
- Commit history uses short, sentence-style messages (e.g., "Update styles", "Add codex instructions").
- Prefer small, focused commits that describe the user-facing change.
- PRs should include:
  - A concise description of what changed and why.
  - Links to related issues or notes.
  - Screenshots for visual/layout changes.

## Agent-Specific Notes
- `codex_instructions.md` documents the generator workflow and file roles; follow it when editing data or templates.
- After any data/template/CSS change, re-run `python generate_site.py` so generated pages stay in sync.
