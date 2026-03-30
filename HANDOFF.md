# Handoff Summary

**Date:** 2026-03-30
**Session focus:** Two tasks -- (1) syncing vita.bib between repos, (2) uploading updated causal inference syllabus

## Key Decisions

- **`~/repos/vita/vita.bib` is the authoritative BibTeX file.** The site's `data/vita.bib` should be a copy of it. When the vita repo version is updated, copy it over and regenerate.
- The vita repo uses `Last, First` author name format (BibDesk convention). The site's `format_authors()` was updated to detect and flip this to `First Last` for display.
- Before copying the vita repo version over, we backfilled four items from the site's version that were missing from the vita repo.
- Syllabus PDFs are uploaded to S3, not stored in this repo. The teaching page links to S3 URLs directly.

## Files Changed and Why

### In this repo (`jake_site_new`)

| File | Change |
|------|--------|
| `data/vita.bib` | Replaced with copy from `~/repos/vita/vita.bib` (after backfilling missing content into that file). Author names are now in `Last, First` format throughout. |
| `generate_site.py` | Added `flip_author_name()` helper (lines ~106--111) that converts `Last, First` to `First Last`. Updated `format_authors()` to call it on each author part. |
| `publications.html` | Regenerated from updated vita.bib. |

Committed and pushed as `16dc8ef` on `main`.

### In the vita repo (`~/repos/vita`)

| File | Change |
|------|--------|
| `vita.bib` | Added 4 items that existed in the site's copy but were missing: (1) `uva2026future` entry (UVA School of Data Science talk, March 2026), (2) DOI for `zomba2025scid` (Grady et al.), (3) DOI for `wong2025maps` (Wong et al.), (4) URL for `yokum2024ap` (Yokum & Bowers). Also fixed typo "Virgina" to "Virginia" in the new entry. **Not committed** -- the vita repo has uncommitted changes. |

### On S3 (`static.jakebowers.org`)

| S3 path | Change |
|---------|--------|
| `MISC/ps531s26_causal.pdf` | Replaced with updated syllabus from `~/repos/CLASSES/531-causal-inference-syllabus/syllabus.pdf` (dated 2026-03-25). Uploaded with `--acl public-read`. |

No site repo changes were needed for the syllabus -- the URL in `data/teaching.yaml` (line 5) already pointed to `ps531s26_causal.pdf`.

## What's Done

- Backfilled missing DOIs, URLs, and the `uva2026future` entry into `~/repos/vita/vita.bib`
- Copied updated vita.bib to `data/vita.bib`
- Updated `format_authors()` to handle `Last, First` author format
- Regenerated site and verified output (42 author names render correctly)
- Committed and pushed all site repo changes
- Uploaded updated causal inference syllabus PDF to S3

## What Remains

- **`~/repos/vita/vita.bib` has uncommitted changes** (the 4 backfilled items). The user may want to commit those in the vita repo.

## Current Blockers / Open Questions

- **BibTeX key mismatch:** The site's old copy used `rabb2021pnas` for the Rabb et al. PNAS paper; the vita repo uses `rabb2021no` for the same entry. Since nothing in the site code references entries by key (it filters by keywords), this is harmless. But if anything ever does key-based lookups, this difference could matter.

## Important Context to Preserve

- **Vita source repo:** `~/repos/vita/` -- contains LaTeX source (`bowers-vita.tex`), compiled PDF, and `vita.bib`.
- **Workflow for vita.bib updates:** Edit `~/repos/vita/vita.bib` as the single source of truth, then `cp ~/repos/vita/vita.bib data/vita.bib` and `uv run python generate_site.py` to update the site.
- **Author format convention:** The vita repo uses `Last, First` (BibDesk default). The site's `flip_author_name()` handles conversion. Both `First Last` and `Last, First` inputs work -- the function checks for a comma.
- **Causal inference syllabus source:** `~/repos/CLASSES/531-causal-inference-syllabus/syllabus.pdf`. Upload command:
  ```bash
  aws s3 cp ~/repos/CLASSES/531-causal-inference-syllabus/syllabus.pdf s3://static.jakebowers.org/MISC/ps531s26_causal.pdf --acl public-read
  ```
- **Upload command for vita PDF** (must include `--acl public-read`):
  ```bash
  aws s3 cp ~/repos/vita/bowers-vita.pdf s3://static.jakebowers.org/MISC/bowers-vita.pdf --acl public-read
  ```
- The bucket `static.jakebowers.org` has no bucket policy -- public access is controlled per-object via ACLs. Without `--acl public-read`, uploaded files will be private and return 403 errors.
