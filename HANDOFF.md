# Handoff Summary

**Date:** 2026-03-30
**Session focus:** Four tasks -- (1) syncing vita.bib between repos, (2) uploading updated causal inference syllabus, (3) setting up Cloudflare cache purging, (4) updating project descriptions on the site

## Key Decisions

- **`~/repos/vita/vita.bib` is the authoritative BibTeX file.** The site's `data/vita.bib` should be a copy of it. When the vita repo version is updated, copy it over and regenerate.
- The vita repo uses `Last, First` author name format (BibDesk convention). The site's `format_authors()` was updated to detect and flip this to `First Last` for display.
- Before copying the vita repo version over, we backfilled four items from the site's version that were missing from the vita repo.
- Syllabus PDFs are uploaded to S3, not stored in this repo. The teaching page links to S3 URLs directly.
- **Cloudflare sits in front of `static.jakebowers.org`.** After uploading files to S3, the Cloudflare cache must be purged or you'll keep seeing the old version (default TTL is 2 hours). A purge script was added to `scripts/purge-cache.sh`.
- **Project descriptions should use paper abstracts** rather than ad-hoc summaries. For the manytests and combined Stephenson papers, the abstract was pulled from `abstract.tex`. For the fully specified BF paper, the abstract was pulled from `Paper/abstract.md` (the user dislikes the current `.tex` abstract; `abstract.md` was written for the website).

## Files Changed and Why

### In this repo (`jake_site_new`)

| File | Change |
|------|--------|
| `data/vita.bib` | Replaced with copy from `~/repos/vita/vita.bib` (after backfilling missing content). Committed and pushed. |
| `generate_site.py` | Added `flip_author_name()` helper (lines ~106--111) that converts `Last, First` to `First Last`. Committed and pushed. |
| `data/projects.yaml` | Three updates: (1) "Detecting Where Effects Occur" -- title updated to match paper, description replaced with abstract from `~/repos/manytests-paper/Paper/abstract.tex`. (2) "Randomization Tests for Distributions" -- description replaced with abstract from `~/repos/combined_stephenson_tests/abstract.tex`. (3) **New entry:** "Fully Specified Bayes Factors for Hypothesis Testing in Qualitative Research" -- added above the Lopez & Bowers p-values paper, description from `~/repos/fully_specified_bf/Paper/abstract.md`. **Not yet committed.** |
| `publications.html` | Regenerated. Committed and pushed. |
| `projects.html` | Regenerated from updated projects.yaml. **Not yet committed.** |
| `scripts/purge-cache.sh` | **New file.** Purges Cloudflare cache for URLs on `static.jakebowers.org`. Requires `CLOUDFLARE_PURGE_TOKEN` env var. **Not yet committed.** |

### In the vita repo (`~/repos/vita`)

| File | Change |
|------|--------|
| `vita.bib` | Added 4 items that existed in the site's copy but were missing: (1) `uva2026future` entry (UVA School of Data Science talk, March 2026), (2) DOI for `zomba2025scid` (Grady et al.), (3) DOI for `wong2025maps` (Wong et al.), (4) URL for `yokum2024ap` (Yokum & Bowers). Also fixed typo "Virgina" to "Virginia". **Not committed.** |

### On S3 (`static.jakebowers.org`)

| S3 path | Change |
|---------|--------|
| `MISC/ps531s26_causal.pdf` | Replaced with updated syllabus from `~/repos/CLASSES/531-causal-inference-syllabus/syllabus.pdf` (dated 2026-03-25). Uploaded with `--acl public-read`. Cloudflare cache purged and verified (MD5 match confirmed). |

## What's Done

- Backfilled missing DOIs, URLs, and the `uva2026future` entry into `~/repos/vita/vita.bib`
- Copied updated vita.bib to `data/vita.bib`
- Updated `format_authors()` to handle `Last, First` author format
- Regenerated site and verified output (42 author names render correctly)
- Committed and pushed vita.bib and generate_site.py changes
- Uploaded updated causal inference syllabus PDF to S3
- Installed Cloudflare wrangler CLI (`brew install cloudflare-wrangler2`), logged in via `wrangler login`
- Created `scripts/purge-cache.sh` for cache purging
- Successfully purged Cloudflare cache for the syllabus PDF and verified the new version is served
- Updated project descriptions in `data/projects.yaml`:
  - "Detecting Where Effects Occur by Testing Hypotheses in Order" -- title and description updated from `~/repos/manytests-paper/Paper/abstract.tex`
  - "Randomization Tests for Distributions of Individual Treatment Effects" -- description updated from `~/repos/combined_stephenson_tests/abstract.tex`
  - "Fully Specified Bayes Factors for Hypothesis Testing in Qualitative Research" -- new entry, description from `~/repos/fully_specified_bf/Paper/abstract.md`
- Regenerated site after each projects.yaml change

## What Remains

- **`data/projects.yaml`, `projects.html`, `scripts/purge-cache.sh`, and `HANDOFF.md` are not yet committed** in this repo.
- **`~/repos/vita/vita.bib` has uncommitted changes** (the 4 backfilled items).
- **`CLOUDFLARE_PURGE_TOKEN` needs to be added to the user's shell profile** (e.g., `~/.zshrc`) for the purge script to work in future sessions.
- **The Cloudflare API token should be rotated** -- it was pasted into this conversation. Go to https://dash.cloudflare.com/profile/api-tokens, delete the current token, create a new one with the same "Purge Cache" permissions for `jakebowers.org`, and update `CLOUDFLARE_PURGE_TOKEN`.

## Current Blockers / Open Questions

- **BibTeX key mismatch:** The site's old copy used `rabb2021pnas` for the Rabb et al. PNAS paper; the vita repo uses `rabb2021no` for the same entry. Since nothing in the site code references entries by key (it filters by keywords), this is harmless. But if anything ever does key-based lookups, this difference could matter.

## Important Context to Preserve

- **Vita source repo:** `~/repos/vita/` -- contains LaTeX source (`bowers-vita.tex`), compiled PDF, and `vita.bib`.
- **Workflow for vita.bib updates:** Edit `~/repos/vita/vita.bib` as the single source of truth, then `cp ~/repos/vita/vita.bib data/vita.bib` and `uv run python generate_site.py` to update the site.
- **Author format convention:** The vita repo uses `Last, First` (BibDesk default). The site's `flip_author_name()` handles conversion. Both `First Last` and `Last, First` inputs work -- the function checks for a comma.
- **Project description sources:** Abstracts for project blurbs come from paper repos:
  - Manytests: `~/repos/manytests-paper/Paper/abstract.tex`
  - Combined Stephenson: `~/repos/combined_stephenson_tests/abstract.tex`
  - Fully specified BF: `~/repos/fully_specified_bf/Paper/abstract.md`
- **Cloudflare caching:** `static.jakebowers.org` is proxied through Cloudflare (Zone ID: `00d57633940d082931a9137e7185e73a`). After any S3 upload, purge the cache:
  ```bash
  ./scripts/purge-cache.sh MISC/filename.pdf
  ```
- **Workflow for uploading static files to S3** (always include `--acl public-read`, then purge cache):
  ```bash
  # Syllabus
  aws s3 cp ~/repos/CLASSES/531-causal-inference-syllabus/syllabus.pdf s3://static.jakebowers.org/MISC/ps531s26_causal.pdf --acl public-read
  ./scripts/purge-cache.sh MISC/ps531s26_causal.pdf

  # Vita PDF
  aws s3 cp ~/repos/vita/bowers-vita.pdf s3://static.jakebowers.org/MISC/bowers-vita.pdf --acl public-read
  ./scripts/purge-cache.sh MISC/bowers-vita.pdf
  ```
- The bucket `static.jakebowers.org` has no bucket policy -- public access is controlled per-object via ACLs. Without `--acl public-read`, uploaded files will be private and return 403 errors.
- **Wrangler CLI** is installed (`brew install cloudflare-wrangler2`) and authenticated via OAuth. The OAuth token does NOT have cache purge permissions -- that's why the separate API token (`CLOUDFLARE_PURGE_TOKEN`) is needed.
