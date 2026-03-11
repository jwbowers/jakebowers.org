# Handoff Summary

**Date:** 2026-03-11
**Session focus:** Uploading updated vita PDF to S3

## Key Decisions

- The vita PDF (`bowers-vita.pdf`) is hosted on **AWS S3**, not on GitHub. The bucket is `static.jakebowers.org` and the file lives at `MISC/bowers-vita.pdf`.
- The site links to `https://static.jakebowers.org/MISC/bowers-vita.pdf` from the nav bar (via `templates/layout.html`) and the index page (via `templates/index.html`).
- No files in this repo were changed. The upload was done externally via `aws s3 cp`.

## Files Changed and Why

No files in this repository were modified during this session.

## What's Done

- Uploaded `~/repos/vita/bowers-vita.pdf` to `s3://static.jakebowers.org/MISC/bowers-vita.pdf` using the AWS CLI.
- Confirmed the AWS CLI is installed at `/opt/homebrew/bin/aws` (v2.34.6) and that the bucket name is `static.jakebowers.org`.

## What Remains

Nothing outstanding from this session.

## Current Blockers / Open Questions

None.

## Important Context to Preserve

- **Vita source repo:** `~/repos/vita/` — contains LaTeX source (`bowers-vita.tex`), compiled PDF, and a short version (`bowers-vita-short.pdf`).
- **Upload command for future vita updates** (must include `--acl public-read`):
  ```bash
  aws s3 cp ~/repos/vita/bowers-vita.pdf s3://static.jakebowers.org/MISC/bowers-vita.pdf --acl public-read
  ```
- The bucket `static.jakebowers.org` has no bucket policy — public access is controlled per-object via ACLs. Without `--acl public-read`, uploaded files will be private and return 403 errors.
- `data/config.yaml` has `vita_pdf: vita.pdf` but this value is **not currently used** by the templates — they hardcode the S3 URL instead. If the hosting ever changes, both `templates/layout.html` and `templates/index.html` would need updating.
