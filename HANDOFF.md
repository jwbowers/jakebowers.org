# Handoff Summary

**Date:** 2026-05-20
**Session focus:** Rewrite the Future Politics page (`data/future_politics.md`) using Jake's style guide; collapse three weak sub-headings into one bulleted "Talks, Interviews, and Collaborations" list; teach the minimal Markdown renderer to handle `- ` lists; commit and push.

## Key Decisions

- **Edited prose against the named offenders in `~/.claude/CLAUDE.md`.** Replaced nominalized openers ("the aim of a teacher is to..."), vague evaluative verbs ("played a role," "envision"), gauzy abstractions ("ways to train the mind to confront the future"), and the locative figure "in the face of." Tightened "seeking ways to understand and judge" -> "judge"; "in an effort to develop" -> "to build"; "the utility of reading Marx" -> "why Marx is worth reading." Kept all facts, links, dates, and people. The William Gibson quote is untouched.
- **Pinned the two flagged verbs with Jake.** "I played a role in the Brave New World conference" -> "I was invited to speak at..."; "helped John Ahlquist envision the UCSD San Diego 2049 event" -> "helped John Ahlquist conceive the...event." Jake supplied both verbs in-session; do not regress them.
- **Collapsed three thematic sub-sections into one list.** "Politics of the Future," "Admiravel Mundo Novo," and "Other Activities" each had only one or two items, and the Admiravel header in particular grouped items (Publico interview, Casa Jasmina/IoT essay) that had nothing to do with the Brave New World conference. Replaced with a single `### Talks, Interviews, and Collaborations` section in rough chronological order: 2014 Duke workshop -> 2015 Porto conference + Sterling video -> Publico interview -> Casa Jasmina/IoT essay with Cara Wong -> ABC Radio National -> UCSD San Diego 2049.
- **Extended `render_markdown()` rather than inlining raw HTML.** The minimal renderer in `generate_site.py` previously knew only H1-H3, paragraphs, and inline links. Added detection for blocks where every line begins with `- ` and emit them as `<ul><li>...</li></ul>`. Kept the addition self-contained inside `render_markdown` so existing pages (bio, project descriptions via `render_markdown_links`) are unaffected.
- **Fixed "Australia National Radio" -> "Australian National Radio".** Jake confirmed; the network is ABC Radio National, the broader phrasing "Australian National Radio's [program]" is what the site uses.
- **Split into two commits.** The Future Politics work is one commit; a second commit resyncs `projects.html`, whose generated HTML had been stale relative to `data/projects.yaml` since commit `2de7945` ("Updates to backburner projects"). Splitting keeps the editorial change separate from a pure regeneration.

## Files Changed and Why

| File | Change |
|------|--------|
| `data/future_politics.md` | Rewrote paragraphs 1 and 2 (course description, Gibson). Replaced the three sub-headings ("Politics of the Future," "Admiravel Mundo Novo," "Other Activities") with one `### Talks, Interviews, and Collaborations` bulleted list of six items in rough chronological order. Pinned verbs "spoke at" (Brave New World) and "conceive" (UCSD 2049). Fixed "Australia" -> "Australian". |
| `generate_site.py` | Added bulleted-list support to `render_markdown()`: if every non-empty line in a block starts with `- `, emit `<ul><li>...</li></ul>` with link rendering applied per item. Docstring updated. |
| `CLAUDE.md` (project) | Updated the `render_markdown()` line to note "bulleted lists with `- `" in the supported subset. |
| `future-politics.html` | Regenerated. |
| `projects.html` | Regenerated to match `data/projects.yaml` at HEAD. The YAML had already been updated in commit `2de7945`; the HTML had been left stale. No semantic change beyond what is already in the YAML. |

## What's Done

- Committed and pushed to `origin/main`:
  - `69e83f4` --- Rewrite Future Politics page and add list support to renderer
  - `8f511e0` --- Regenerate projects.html to match YAML
- `.github/workflows/build.yml` will auto-deploy to `gh-pages` on push to `main`.
- Verified the rendered HTML: `future-politics.html` contains a single `<h3>Talks, Interviews, and Collaborations</h3>` followed by a `<ul>` with six `<li>` items, each with the expected links intact.

## What Remains

- **Nothing follow-up specific to this session.** The Future Politics page reads as Jake wants it; the list-support extension is minimal and isolated.
- **From prior session (still pending):** Migrating the 99 PDFs in `static/papers/` to S3. Plan is unchanged.

## Open Questions

- None outstanding. Earlier in the session I had asked whether to drop the "Other Activities" heading and fold its items into the preceding paragraph, or rename it; Jake's "let's combine into a list" answer resolved it.

## Important Context to Preserve

- **`render_markdown()` now supports bulleted lists.** A block is treated as a `<ul>` only if *every* non-empty line starts with `- ` (two characters: hyphen + space). Mixed blocks (some `- ` lines and some prose lines) will fall through to the paragraph branch and render as one `<p>`. If you need lists with leading prose, separate them with a blank line. This contract is intentional: it keeps the renderer easy to reason about, and matches the existing block-splitting on `\n\n`.
- **Markdown subset is still minimal.** Supported: H1-H3 (`#`, `##`, `###`), paragraphs (default), inline links `[text](url)`, and now bulleted lists with `- `. Not supported: emphasis (`*x*`, `_x_`), code spans/blocks, blockquotes, ordered lists, nested lists, images, tables. If a future edit needs any of these, extend the renderer; do not switch to a full Markdown library without checking with Jake (the custom renderer was a deliberate choice).
- **ASCII-only convention is non-negotiable.** Jake's global CLAUDE.md forbids unicode (em dash, en dash, smart quotes, ellipsis, arrows, decorative bullets) in any file written or edited. Use `---` for em dash, `--` for en dash, straight quotes, `...` for ellipsis, `->` for arrow. The only documented exception is diacritics on personal names (e.g., "Lopez").
- **Style-guide hits relevant to future writing edits.** Jake's writing rules call out by name: nominalizations, passive voice that hides the actor, jargon-for-its-own-sake, architectural/anatomical metaphors used decoratively ("load-bearing," "spine," "scaffolding"), industrial metaphors ("the machinery of," "the apparatus of"), vague evaluative judgments ("is appropriate," "is suitable," "is reasonable," "is warranted," "is comfortable"), locative figures that hide a plain verb ("reads onto," "maps onto," "lives in"), and ornamental transitions ("Moreover," "Furthermore," "It is important to note that"). When editing Jake's prose, run a pass against these specifically.
- **Do not put words in cited authors' mouths.** The Cascio paraphrase was preserved across the rewrite ("futurism is not prediction but mental readiness") because the original prose framed it as paraphrase, not quotation. Any sharper framing would need to be checked against Cascio's actual phrasing.
- **Build/deploy unchanged.** `uv run python generate_site.py` regenerates HTML in repo root. `.github/workflows/build.yml` watches `main` and pushes generated HTML to `gh-pages`.
- **Static file hosting unchanged.** PDFs at `https://static.jakebowers.org/`, S3 bucket `static.jakebowers.org`, no bucket policy, per-object ACLs (`--acl public-read` required on upload). Cloudflare proxy in front of the bucket; purge with `./scripts/purge-cache.sh <path>`.
- **`www.jakebowers.org` is dead for static files.** Every URL of the form `https://www.jakebowers.org/<path>` returns 404. Do not reintroduce.
- **Generated HTML can drift from YAML.** This session caught `projects.html` stale relative to `data/projects.yaml` (commit `2de7945` updated the YAML but did not regenerate). The auto-deploy workflow regenerates on push, but if a coauthor edits YAML in another repo or branch and you pull, run `uv run python generate_site.py` and commit any HTML drift in a separate "regenerate" commit so the diff stays readable.
- **Archive source for any future link forensics:** `~/repos/Archive/jakebowers.org/` holds the original static site files from the dead `www.jakebowers.org` domain. `TeachingStuff/` subdir holds most of the old `ps230f*syl.pdf` files.

## Cross-repo work this session

None. All edits were in `~/repos/jake_site_new`.
