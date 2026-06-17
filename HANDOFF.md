# Handoff Summary

**Date:** 2026-06-17
**Session focus:** Link two missing publication PDFs (Hansen & Bowers 2008, Rabb et al. 2021) and fix a broken DOI; establish `data/vita.bib` as a derived mirror of the canonical private vita repo with a sync script and a weekly drift check; make the vita cache-busting tag content-based instead of a timestamp; credit Claude Code in the acknowledgements. One self-inflicted outage along the way (gitignoring the generated HTML), caught and fixed within the session.

## Commits this session (all pushed to `origin/main`, in order)

- `824bb0b` --- Link Hansen and Bowers 2008 PDF and fix its DOI link
- `4abc2de` --- Link Rabb et al. 2021 PNAS PDF, drop orphaned duplicate
- `f83951f` --- Stop tracking generated HTML pages **(this was a mistake; see Incident below)**
- `a1a766c` --- Add vita.bib sync script and document the canonical bib source
- `8df1ef5` --- Sync vita.bib mirror with canonical
- `bb29100` --- Add launchd wrapper for weekly vita.bib drift check
- `1345aa6` --- Restore tracking of generated HTML pages to fix broken deploy **(the fix for `f83951f`)**
- `ff7a049` --- Make vita cache-bust tag a content hash, not a timestamp
- `f1a0d03` --- Credit Claude Code in the site acknowledgements

History note: these six original commits were rebased onto `origin/main` mid-session because someone pushed `92cfc42 "Update projects.yaml"` (a one-line arXiv URL add) from elsewhere while work was in progress. The rebase was clean (disjoint files). Hashes above are the final pushed ones; any earlier hashes are obsolete.

Cross-repo: `~/repos/vita` got commit `3519baa "Fix hansen2008cbs DOI URL to resolvable https form"` on branch **`master`** (not `main`), pushed to `git@github.com:jwbowers/vita.git`.

## CRITICAL Incident and lesson (read before touching the build/deploy)

**Do NOT add the generated root HTML pages to `.gitignore`. Doing so takes the entire live site down.**

What happened: reasoning that "CI regenerates the HTML on every push, so the committed copies never ship," the generated pages (`index.html`, `publications.html`, `projects.html`, `teaching.html`, `future-politics.html`) were gitignored and `git rm --cached`'d (commit `f83951f`). After push, every page on jakebowers.org returned 404.

Why: the deploy step is `peaceiris/actions-gh-pages` with `publish_dir: ./`, and it publishes **only git-tracked files**. CI does regenerate the HTML (so the *content* that ships is always freshly built from `data/` + `templates/`), but a file must be *tracked* to be included in the deploy at all. The committed HTML's tracking status was load-bearing for the deploy; the earlier reasoning conflated "content shipped" with "file included." Tracked files (the `static/papers/*.pdf`) deployed fine; the now-ignored HTML was dropped, and `gh-pages` ended up with zero HTML.

Fix (commit `1345aa6`): re-tracked all five pages, removed them from `.gitignore`, and corrected `CLAUDE.md`, `AGENTS.md`, `codex_instructions.md` to state the pages must stay tracked and be committed after each regeneration, with an explicit "do not gitignore" warning. Verified `gh-pages` had the HTML back and the live root/pages returned 200.

If the timestamp-churn that motivated the untracking ever needs solving again: the right tool is NOT gitignore. It was solved this session by making the cache-bust tag content-derived (see below). The other option (publish from a separate `_site/` dir so the deploy is not filtered by repo tracking) is a CI change that must be tested carefully given this incident.

## Key Decisions

- **PDFs resolve by BibTeX-key slug.** `static/papers/hansen2008cbs.pdf` and `static/papers/rabb2021no.pdf` are named to match their `@article{...}` keys, so `resolve_pdf_url()` in `generate_site.py` finds them automatically. The `data/publication_pdfs.yaml` map exists only for the three files whose names do not match their keys; matching the key is the dominant convention (96 of ~100 PDFs).
- **Fixed two broken DOI links** `doi:10.1214/08-STS254` -> `https://doi.org/10.1214/08-STS254` on `hansen2008cbs`, in both the site mirror and the canonical vita repo. A bare `doi:` string is not a clickable URL.
- **Removed an orphaned duplicate.** `static/papers/rabb2021pnas.pdf` was the same published paper as `rabb2021no` (same title, same 2 pages) but named with a `pnas` convention that matched no key and collided conceptually with the separate `rabb2022pnas` entry. Replaced by the user's new `rabb2021no.pdf`; git recorded it as a rename, preserving history. The user confirmed removal.
- **`data/vita.bib` is now a derived mirror, not a source of truth.** The canonical bibliography is `~/repos/vita/vita.bib` in the private repo `github.com:jwbowers/vita` (branch `master`), where Jake normally adds entries. Because that repo is private, CI cannot fetch it at build time, so the mirror stays committed here and is refreshed by hand via `bin/sync-vita-bib.sh`.
- **Cache-bust tag is content-derived, not time-derived.** Previously `vita_version = datetime.now().strftime('%Y%m%d%H%M')`, which rewrote all five pages on every regeneration. Now it is a 12-char SHA-256 of the canonical vita PDF, persisted in `config.yaml`. Regenerating without changing the vita produces no diff.
- **Credited Claude Code alongside OpenAI Codex** in the front-page acknowledgements (in the template, then regenerated).

## Files Changed and Why

| File | Change |
|------|--------|
| `data/vita.bib` | Fixed `hansen2008cbs` DOI; synced with canonical to pull in two new 2026 entries (`delao2026barriers`, `bowers2026aoas`) and two upstream typo fixes (`Pontificia`, `University`). Now byte-identical to `~/repos/vita/vita.bib`. |
| `static/papers/hansen2008cbs.pdf` | New. Linked PDF for the Statistical Science covariate-balance paper. |
| `static/papers/rabb2021no.pdf` | New (replaced orphaned `rabb2021pnas.pdf`). Linked PDF for the PNAS paper. |
| `bin/sync-vita-bib.sh` | New. Check (default, read-only) or `--apply` sync of canonical -> mirror; refuses to clobber mirror-only lines unless `--force`. See "vita.bib mirror" below. |
| `bin/vita-bib-check-notify.sh` | New. Wraps the check, logs to `~/Library/Logs/vita-bib-check.log`, posts a macOS notification on drift. Invoked by the launchd agent. |
| `data/config.yaml` | Added `vita_pdf_source` (local PDF path for hashing) and `vita_version` (the content-hash tag; auto-maintained, do not hand-edit). |
| `generate_site.py` | Added `import hashlib`, `resolve_vita_version()`, `_persist_vita_version()`; replaced the timestamp cache-bust with the content hash. |
| `CLAUDE.md`, `AGENTS.md`, `codex_instructions.md` | Added the bib-mirror workflow and the cache-bust mechanism; corrected the HTML-tracking guidance after the incident (pages stay tracked, committed each regen, never gitignored). |
| `templates/index.html` | Added Claude Code to the acknowledgements line. |
| `index.html`, `publications.html`, `projects.html`, `teaching.html`, `future-politics.html` | Regenerated and committed (they are tracked; the deploy needs them). |

## The vita.bib mirror system (how to keep the two bibs in sync)

- **Source of truth:** `~/repos/vita/vita.bib` (private, branch `master`). Edit there.
- **Mirror:** `data/vita.bib` here. Do not hand-edit it.
- **Sync:** `./bin/sync-vita-bib.sh` (no args) checks drift, read-only, exit 0 if in sync / 1 if diverged. `--apply` copies canonical -> mirror but refuses if the mirror has lines absent from the canonical (a sign of a direct edit that should be ported upstream first); `--apply --force` overrides after you confirm those lines are stale. Override the canonical path with the `VITA_BIB` env var.
- **If you ever fix something in the mirror,** port it to the canonical and re-sync; otherwise the next sync reverts it. (That is exactly what the `hansen2008cbs` DOI fix required this session.)
- **Limitation:** a plain text diff cannot tell a real mirror edit from stale text, so the script surfaces all mirror-only lines for human judgment rather than auto-resolving.
- **Weekly check:** launchd agent `~/Library/LaunchAgents/org.jakebowers.vita-bib-check.plist` runs `bin/vita-bib-check-notify.sh` **Mondays at 9:00am**, logs to `~/Library/Logs/vita-bib-check.log`, and pops a macOS notification only on drift. Verified it runs (logged `exit=0 / in sync`). The plist is machine config, not tracked in the repo. Manage with `launchctl bootout`/`bootstrap gui/$(id -u) <plist>`. NOT yet confirmed in a real-drift scenario: macOS sometimes routes `osascript` notifications through "Script Editor" and suppresses them; the log always records the result regardless. It also only fires when the Mac is awake.

## The cache-bust tag (how the vita link `?v=` works now)

- `templates/layout.html` and `templates/index.html` link the vita as `.../bowers-vita.pdf?v=<tag>`. The tag busts Cloudflare/browser caches when a new vita is uploaded.
- `resolve_vita_version()` computes a SHA-256 (first 12 hex) of `vita_pdf_source` (default `~/repos/vita/bowers-vita.pdf`). If that file is present (Jake's machine) and the hash changed, it writes the new value into `config.yaml` `vita_version` (targeted line edit, preserves comments) and uses it.
- When the PDF is absent (CI runner), it reuses the committed `vita_version`. CI builds the deployed site, so that committed value is what ships -- which is why the hash is persisted rather than recomputed fresh each run. Falls back to `"1"` if neither PDF nor stored value exists.
- **Vita-update workflow** (now in CLAUDE.md): `aws s3 cp ~/repos/vita/bowers-vita.pdf s3://static.jakebowers.org/MISC/bowers-vita.pdf --acl public-read` then `python generate_site.py` (auto-bumps `vita_version` + the HTML), then commit `config.yaml` and the pages.

## What's Done

- Both PDFs linked, live, and serving 200; both DOI links resolve. Verified on `gh-pages` and live.
- `data/vita.bib` synced with canonical; DOI fix ported upstream and pushed to the vita repo.
- Sync script + launchd weekly check installed and verified.
- Cache-bust tag is content-based; verified double-regeneration produces byte-identical HTML (no churn). Confirmed only the actually-changed page diffs now (the acknowledgement edit touched only `index.html`).
- Site restored after the gitignore incident; all CI runs green; everything pushed. Working tree clean in both repos.

## What Remains / Open Questions

- **Nothing required.** All this session's goals are complete and deployed.
- **Cosmetic:** after each deploy the live HTML can lag a few minutes behind Cloudflare's cache (the live page may show an older `?v=` timestamp until the cache expires). The deployed `gh-pages` artifact is authoritative and correct. Not a bug.
- **Minor:** commit `ff7a049` is missing the `Co-Authored-By` trailer (forgotten). Left as-is rather than force-push `main` right after an outage.
- **Carried forward from prior sessions (not re-verified this session):** migrating the ~100 PDFs in `static/papers/` to S3 (publication PDFs are currently served from the repo via `static/papers/<file>`, unlike other static files which are on S3). Plan unchanged.

## Important Context to Preserve

- **Deploy publishes only tracked files.** (See the Incident.) Generated root HTML must stay tracked and be committed after every regeneration. Never gitignore them.
- **`data/vita.bib` is a mirror; edit `~/repos/vita/vita.bib`.** (See the mirror system.)
- **`vita_version` in `config.yaml` is auto-maintained; do not hand-edit it.**
- **ASCII-only convention is non-negotiable.** Jake's global CLAUDE.md forbids unicode (em dash, en dash, smart quotes, ellipsis, arrows, decorative bullets) in any file. Use `---` (em dash), `--` (en dash), straight quotes, `...`, `->`. Documented exception: diacritics on personal names (e.g., "Lopez", "Balan").
- **Build/deploy.** `uv run python generate_site.py` regenerates HTML in the repo root. `.github/workflows/build.yml` runs on push to `main`: it installs deps, runs the generator, and `peaceiris/actions-gh-pages` deploys `publish_dir: ./` (tracked files) to `gh-pages`. `CNAME` (custom domain) is tracked and must stay tracked.
- **Static file hosting.** Non-publication static files (vita, syllabi) live on S3 bucket `static.jakebowers.org` (`https://static.jakebowers.org/`), no bucket policy, per-object ACLs --- `--acl public-read` required on upload or files 403. Cloudflare proxies in front. Publication PDFs, by contrast, are served from this repo at `static/papers/<file>` and deployed via gh-pages.
- **`render_markdown()` subset (still minimal).** Supports H1-H3, paragraphs, inline links `[text](url)`, and bulleted lists where *every* non-empty line in a block starts with `- `. Not supported: emphasis, code, blockquotes, ordered/nested lists, images, tables. Extend the custom renderer rather than swapping in a full Markdown library without checking with Jake.
- **`safe_year()` in `generate_site.py` must not be removed** (parses BibTeX years like `{2006}`; prevents crashes).
- **Publication filtering keywords:** `peer_reviewed`, `technical_report`, `open_source`, `essay`. `@unpublished` entries go to projects, not publications. New `under_review` `@article` entries (e.g. the two 2026 additions) render nowhere on the site (no matching filter) --- harmless but inert.
- **Writing-style hits for any prose edits** (from Jake's global CLAUDE.md): avoid nominalizations, actor-hiding passives, jargon-for-its-own-sake, decorative architectural/anatomical/industrial metaphors ("load-bearing," "spine," "scaffolding," "the machinery of"), vague evaluative judgments ("is appropriate/suitable/reasonable/warranted/comfortable"), locative figures ("reads onto," "maps onto," "lives in"), folksy idioms ("shore up," "fold in"), and throat-clearing ("it is important to note that"). Do not put words in cited authors' mouths.
- **Carried over (not re-verified this session):** Cloudflare cache purge reportedly via `./scripts/purge-cache.sh <path>`; `www.jakebowers.org` is dead for static files (404s); archive of the old site at `~/repos/Archive/jakebowers.org/` (`TeachingStuff/` holds old `ps230f*syl.pdf`). Confirm these still hold before relying on them.

## Cross-repo work this session

- `~/repos/vita` (private, branch `master`): committed and pushed `3519baa` porting the `hansen2008cbs` DOI fix upstream so the next mirror sync would not revert it.
