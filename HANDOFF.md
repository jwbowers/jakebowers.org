# Handoff Summary

**Date:** 2026-03-30
**Session focus:** Move non-PDF static files out of git and onto S3, add replication archive links to publications page.

## Key Decisions

- **Non-PDF archives in `static/papers/` belong on S3, not in git.** They were uploaded to `s3://static.jakebowers.org/papers/` with `--acl public-read` and removed from git tracking. The `.gitignore` now excludes `*.tar.gz`, `*.tgz`, `*.zip`, and `*.rnw` from `static/papers/`.
- **Two `paper-archive` tarballs were both replication archives for Hansen & Bowers 2009 JASA.** We kept the newer one (Sept 26, 2008) and deleted the older one (Sept 3, 2008) from disk entirely.
- **Replication archives should be linked from the publications page.** A new `replication-url` BibTeX field was added to the relevant entries, and the site generator and template were updated to render `[replication]` links alongside existing `[link]` and `[pdf]` links.
- **The 99 PDF files in `static/papers/` remain tracked in git for now.** Moving them to S3 is the logical next step but was deferred to a future session.

## Files Changed and Why

### In this repo (`jake_site_new`)

| File | Change |
|------|--------|
| `data/vita.bib` | Added `replication-url` field to 4 entries: `hansenbowers2009att` (JASA), `bowers2005eda` (EDA for HLM), `bowers2004tpm` (TPM), `bowers2011mem` (Making Effects Manifest). |
| `generate_site.py` | Added extraction of `replication-url` from BibTeX entries and passes `replication_url` through to publication display items (~line 376). |
| `templates/publications.html` | Added `[replication]` link rendering after `[pdf]` link (line 50). |
| `publications.html` | Regenerated. Four publications now show `[replication]` links. |
| `.gitignore` | Added `__pycache__/` and non-PDF archive patterns under `static/papers/`. |
| `static/papers/` | 6 files removed from git tracking via `git rm --cached`: `ManifestEffects_1.0.tar.gz`, `bowersTPM.rnw`, `bowersTPM.zip`, `bowersdrakesource.tar.gz`, `paper-archive-20080903.tgz`, `paper-archive-20080926.tar.gz`. |

### On S3 (`static.jakebowers.org/papers/`)

| S3 key | Source file | Paper |
|--------|-------------|-------|
| `papers/bowershansen2008JASA-replication.tar.gz` | `paper-archive-20080926.tar.gz` | Hansen & Bowers 2009, JASA |
| `papers/bowers2005eda-replication.tar.gz` | `bowersdrakesource.tar.gz` | Bowers & Drake 2005, "EDA for HLM" |
| `papers/bowers2004tpm-replication.zip` | `bowersTPM.zip` | Bowers 2004, "Using R to Keep it Simple" (TPM) |
| `papers/bowers2004tpm.rnw` | `bowersTPM.rnw` | Source `.rnw` for same TPM paper |
| `papers/ManifestEffects_1.0.tar.gz` | `ManifestEffects_1.0.tar.gz` | Bowers 2011, "Making Effects Manifest" (R package) |

### Deleted from disk

| File | Reason |
|------|--------|
| `static/papers/paper-archive-20080903.tgz` (62MB) | Older duplicate of the JASA replication archive; the Sept 26 version was kept. |

## What's Done

- Uploaded 5 non-PDF files to S3 with `--acl public-read`
- Added `replication-url` BibTeX field to 4 publications
- Updated generator and template to render `[replication]` links
- Regenerated site and verified all 4 replication links appear
- Removed all 6 non-PDF files from git tracking
- Updated `.gitignore` to prevent re-adding
- Deleted older duplicate archive from disk
- Committed all changes (commit `8d10203`)

## What Remains

- **99 PDF files (~180MB) are still tracked in git under `static/papers/`.** The plan is to move these to S3 as well, following the same pattern. This requires:
  1. Uploading all PDFs to `s3://static.jakebowers.org/papers/`
  2. Changing `resolve_pdf_url()` in `generate_site.py` to return `https://static.jakebowers.org/papers/{match}` instead of `static/papers/{match}`
  3. Updating `is_pdf_url()` to recognize S3 URLs (it already checks `.pdf` extension, so the `'static/papers/' in lowered` check can be removed)
  4. Running `git rm --cached` on all PDFs and adding `static/papers/*.pdf` to `.gitignore`
  5. Regenerating the site
- **Git history still contains the removed binaries.** Clone size won't shrink until history is rewritten (e.g., `git filter-repo`). This is a separate, more invasive step.
- **From previous session (may still be pending):** `data/projects.yaml`, `projects.html`, `scripts/purge-cache.sh`, and prior `HANDOFF.md` changes may not have been committed. Check `git status`.
- **`~/repos/vita/vita.bib` may have uncommitted changes** (4 backfilled items from the previous session).

## Current Blockers / Open Questions

- None for the completed work. The PDF migration is straightforward but deferred by user preference.

## Important Context to Preserve

- **S3 bucket:** `static.jakebowers.org` -- no bucket policy, public access is per-object via `--acl public-read`. Without this flag, uploads return 403.
- **Cloudflare caching:** The bucket is proxied through Cloudflare (Zone ID: `00d57633940d082931a9137e7185e73a`). After uploading to S3, purge the cache with `./scripts/purge-cache.sh <path>`.
- **Replication URL convention:** Uses the BibTeX field `replication-url`. The generator reads it as `item.get('replication-url')` and passes it as `replication_url` to the template. To add replication links to more papers, just add `replication-url = {https://static.jakebowers.org/papers/filename}` to the BibTeX entry.
- **File naming on S3:** Replication archives were renamed to `{bibtex-key}-replication.{ext}` for clarity, except `ManifestEffects_1.0.tar.gz` which kept its original name (it's an R package).
- **Vita source repo:** `~/repos/vita/` is the authoritative source for `vita.bib`. After editing it there, copy to `data/vita.bib` and regenerate.
