# Handoff Summary

**Date:** 2026-04-28
**Session focus:** Audit and repair every link on `teaching.html`. Migrated all pre-2018 teaching URLs from the dead `www.jakebowers.org` domain to S3, and uploaded four missing 2024-2025 syllabi.

## Key Decisions

- **All available archive PDFs go to `MISC/` (not a new `archive/` prefix).** Keeps S3 layout consistent with the existing convention. The bucket already mixes current and older items in `MISC/` (e.g., `Bowers_Reproducibility_For_Robust_Policy.pdf` from 2021).
- **Three `syllabus.pdf` collisions resolved by prefixing.** The Archive had three generic `PS{230,531,530}/syllabus.pdf` files that would collide in a flat `MISC/` namespace. Uploaded as `ps230syl_archive.pdf`, `ps531syl_archive.pdf`, `ps530syl_archive.pdf`. The `PS590/finalpaperguide.pdf` was renamed to `ps590_finalpaperguide.pdf` for clarity (its sibling `PS531/finalpaperguide.pdf` doesn't exist anywhere, so there was no actual collision, but the prefix removes ambiguity).
- **Old course HTML pages were not migrated.** The six `ps{532,590,688,496,599,389}.html` files in the Archive are course websites from 2003-2007. Their internal links to handouts and assignments are dead. Rather than upload them with broken sub-links, I dropped the URLs from `teaching.yaml` and left the course title as plain text. The Archive copies remain on disk if Jake wants them later.
- **Dead external links dropped (URL only, not the entry).** `stateness.com/es/escuela-de-verano-metodos-mixtos/` (Winter 2015), `polisci.osu.edu/faculty/mcconnaughy.3/index.htm` (Fall 2012), and `psweb.sbs.ohio-state.edu/faculty/jbox/ITV/ITVHome.html` (Fall 2007, Fall 2011, Fall 2012) all 404 or fail to resolve. Course entries kept with title only; the McConnaughy attribution was inlined into the course title for Fall 2012.
- **Four PDFs that don't exist anywhere → URL dropped.** `ps531s12syl.pdf`, `ps531s13syl.pdf`, and `PS531/finalpaperguide.pdf` (referenced 3x) are missing from both S3 and `~/repos/Archive/jakebowers.org/`. Course entries kept as plain titles.

## Files Changed and Why

### In this repo (`jake_site_new`)

| File | Change |
|------|--------|
| `data/teaching.yaml` | Rewrote 27 URLs from `www.jakebowers.org/...` to `static.jakebowers.org/MISC/...`. Dropped URLs for 4 missing PDFs and 6 old HTML course pages. Dropped 3 dead external links. Inlined "co-designed with Corrine McConnaughy" into PS590 Fall 2012 title (was a materials link to her dead OSU page). |
| `teaching.html` | Regenerated from the updated yaml. |

### On S3 (`static.jakebowers.org/MISC/`)

**Step 1 (current 2024-2025 syllabi):** 4 files uploaded with `--acl public-read`:

| S3 key | Source |
|--------|--------|
| `MISC/future_politics_syllabus_2025.pdf` | `static/syllabi/future-politics-ps374-fall-2025.pdf` (in this repo) |
| `MISC/ps530f25syl.pdf` | `~/repos/CLASSES/530-syllabus/syllabus.pdf` (Fall 2025) |
| `MISC/ps531s25syl.pdf` | `~/repos/CLASSES/531-syllabus/syllabus.pdf` (Spring 2025) |
| `MISC/ps531f24syl.pdf` | `~/repos/Tenure/TeachingPortfolio/Syllabi/ps531f24syl.pdf` |

**Step 2 (pre-2018 archive migration):** 25 PDFs uploaded from `~/repos/Archive/jakebowers.org/`. New S3 names listed; sources are at the URL paths shown after `<-`:

- `MISC/ps531syl_archive.pdf` <- `PS531/syllabus.pdf` (used for Spring 2017, Spring 2018)
- `MISC/ps230syl_archive.pdf` <- `PS230/syllabus.pdf` (Spring 2017, Fall 2017)
- `MISC/ps530syl_archive.pdf` <- `PS530/syllabus.pdf` (Fall 2016)
- `MISC/ps230f14syl.pdf` <- `TeachingStuff/ps230f14syl.pdf`
- `MISC/experimentosdecamposyl2014.pdf` <- `experimentosdecamposyl2014.pdf`
- `MISC/matchingUCU2014.pdf` <- `matchingUCU2014.pdf`
- `MISC/causalinfICPSR2014.pdf` <- `causalinfICPSR2014.pdf`
- `MISC/PS522researchdesignspring2014.pdf` <- `PS522/PS522researchdesignspring2014.pdf`
- `MISC/ps531s14syl.pdf` <- `PS531S14/ps531s14syl.pdf`
- `MISC/ps300s14syl.pdf` <- `PS300S14/ps300s14syl.pdf`
- `MISC/ps230f13syl.pdf` <- `TeachingStuff/ps230f13syl.pdf`
- `MISC/ps300f13syl.pdf` <- `PS300F13/ps300f13syl.pdf`
- `MISC/ps300s13syl.pdf` <- `PS300/ps300s13syl.pdf`
- `MISC/ps230f12syl.pdf` <- `TeachingStuff/ps230f12syl.pdf`
- `MISC/ps590-experiments-f12syl.pdf` <- `ps590-experiments-f12syl.pdf`
- `MISC/ps300s12syl.pdf` <- `PS300/ps300s12syl.pdf`
- `MISC/ps230f11syl.pdf` <- `TeachingStuff/ps230f11syl.pdf`
- `MISC/ps590f11syl.pdf` <- `ps590f11syl.pdf`
- `MISC/ps590_finalpaperguide.pdf` <- `PS590/finalpaperguide.pdf`
- `MISC/ps531s11syl.pdf` <- `ps531s11syl.pdf`
- `MISC/ps230s11syl.pdf` <- `TeachingStuff/ps230s11syl.pdf`
- `MISC/ps300f10syl.pdf` <- `PS300/ps300f10syl.pdf`
- `MISC/ps531s10syl.pdf` <- `ps531s10syl.pdf`
- `MISC/ps230s09syl.pdf` <- `TeachingStuff/ps230s09syl.pdf`
- `MISC/ps499s09syl.pdf` <- `ps499s09syl.pdf`

## What's Done

- All 4 broken 2024-2025 S3 URLs (`future_politics_syllabus_2025.pdf`, `ps530f25syl.pdf`, `ps531s25syl.pdf`, `ps531f24syl.pdf`) now return 200.
- All 25 archive PDFs uploaded to S3, all return 200.
- `teaching.yaml` rewritten; site regenerated.
- Committed (`3f144ef`) and pushed to `origin/main`. The build.yml GitHub Action auto-deploys main -> gh-pages, so the live site will update shortly.
- Cloudflare cache purge was not needed for the new uploads (they were not previously cached as 200 responses).

## What Remains

- **Verify the deploy.** GitHub Actions should publish to gh-pages within a minute or two of the push. Loading https://jakebowers.org/teaching.html in a browser will confirm the live site reflects the changes.
- **Files dropped, not deleted.** The 4 missing PDFs (`ps531s12syl.pdf`, `ps531s13syl.pdf`, `PS531/finalpaperguide.pdf`) and the 6 old HTML course pages (`ps{532,590,688,496,599,389}.html`) are still listed in `teaching.yaml` as plain titles without URLs. If any of those files are recovered later, just add a URL line back to the YAML entry.
- **From prior session (still pending):** Migrating the 99 PDFs in `static/papers/` to S3. The plan is in the previous HANDOFF and is unchanged.

## Current Blockers / Open Questions

- None for the completed work.
- One minor judgment call still open: whether to upload the 6 old course HTML pages to S3 anyway (with broken inner links). They have substantive descriptive content even if handouts/assignments don't resolve. Default decision was to drop the URLs; reversible if Jake disagrees.

## Important Context to Preserve

- **`www.jakebowers.org` is dead for static files.** Every URL of the form `https://www.jakebowers.org/<path>` returns 404. Don't reintroduce these URLs; redirect to S3.
- **S3 bucket convention:** `static.jakebowers.org`, no bucket policy, public access is per-object via `--acl public-read`. Without that flag, uploads return 403.
- **Cloudflare caching:** The bucket is proxied through Cloudflare (Zone ID `00d57633940d082931a9137e7185e73a`). After uploading to S3, purge with `./scripts/purge-cache.sh <path>`. Requires `CLOUDFLARE_PURGE_TOKEN` env var. Not needed for fresh uploads to URLs that previously 404'd.
- **Naming for archive collisions:** When uploading multiple files with the same basename to a flat S3 prefix, prefix with course code (e.g., `ps531syl_archive.pdf`).
- **Generic `MISC/` PDFs that look like sibling files might be archive content.** The new `ps{230,530,531}syl_archive.pdf` files in `MISC/` are pre-2018 syllabi; the same-stem files without `_archive` suffix are different (current) syllabi. Don't conflate.
- **Build/deploy:** `uv run python generate_site.py` regenerates HTML in repo root. `.github/workflows/build.yml` watches `main` and pushes generated HTML to `gh-pages`. No manual deploy step.
- **Archive source:** `~/repos/Archive/jakebowers.org/` holds the original static site files from the dead domain. `TeachingStuff/` subdir holds most of the old `ps230f*syl.pdf` files. Useful for further forensic work if more dead URLs surface elsewhere on the site.
