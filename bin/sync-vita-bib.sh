#!/usr/bin/env bash
#
# sync-vita-bib.sh -- keep data/vita.bib in step with the canonical vita repo.
#
# The canonical bibliography lives in ~/repos/vita/vita.bib (override with the
# VITA_BIB environment variable). The copy in this repo, data/vita.bib, is a
# derived mirror: edit the canonical, then run this script to refresh the
# mirror. Do not hand-edit the mirror -- edits there drift out of the canonical
# and get lost on the next sync.
#
# Modes:
#   (default)   Check only. Report whether the two files agree; never writes.
#               Exit 0 if identical, 1 if they differ, 2 on a setup error.
#               Safe to run from cron or by hand at any time.
#   --apply     Copy canonical -> data/vita.bib, but refuse if the mirror holds
#               lines absent from the canonical (a sign someone edited the
#               mirror directly, e.g. a fix that should be ported upstream
#               first).
#   --force     With --apply, overwrite the mirror even when it has unique
#               lines. Use only after confirming those lines are stale.
#   -h, --help  Print this header.

set -euo pipefail

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
repo_root="$(cd "$script_dir/.." && pwd)"
SITE_BIB="$repo_root/data/vita.bib"
CANONICAL_BIB="${VITA_BIB:-$HOME/repos/vita/vita.bib}"

mode="check"
force=0
for arg in "$@"; do
  case "$arg" in
    --apply)  mode="apply" ;;
    --check)  mode="check" ;;
    --force)  force=1 ;;
    -h|--help) sed -n '2,$ { /^#/!q; s/^# \{0,1\}//; p }' "$0"; exit 0 ;;
    *) echo "unknown argument: $arg (try --help)" >&2; exit 2 ;;
  esac
done

if [ ! -f "$CANONICAL_BIB" ]; then
  echo "canonical bib not found: $CANONICAL_BIB" >&2
  echo "(set VITA_BIB to its path; skipping)" >&2
  exit 2
fi
if [ ! -f "$SITE_BIB" ]; then
  echo "site bib not found: $SITE_BIB" >&2
  exit 2
fi

if diff -q "$CANONICAL_BIB" "$SITE_BIB" >/dev/null; then
  echo "in sync: data/vita.bib matches $CANONICAL_BIB"
  exit 0
fi

# They differ. Capture the diff once, then count direction.
# Lines marked '<' are in the canonical only (canonical is ahead).
# Lines marked '>' are in the mirror only (mirror has unique lines).
d="$(diff "$CANONICAL_BIB" "$SITE_BIB" || true)"
canon_only="$(printf '%s\n' "$d" | grep -c '^<' || true)"
site_only="$(printf '%s\n' "$d" | grep -c '^>' || true)"

echo "DIVERGED:"
echo "  $canon_only line(s) in the canonical but not the mirror (canonical is ahead)"
echo "  $site_only line(s) in the mirror but not the canonical (mirror has unique lines)"
echo "  canonical: $CANONICAL_BIB"
echo "  mirror:    $SITE_BIB"

if [ "$mode" = "check" ]; then
  echo
  echo "Run with --apply to copy canonical -> mirror."
  if [ "$site_only" -gt 0 ]; then
    echo "WARNING: the mirror has $site_only unique line(s). Review before applying."
    echo "If any are real edits (not stale text), port them to the canonical first."
    echo
    echo "diff (canonical '<' vs mirror '>'):"
    printf '%s\n' "$d"
  fi
  exit 1
fi

# apply mode
if [ "$site_only" -gt 0 ] && [ "$force" -ne 1 ]; then
  echo
  echo "REFUSING to overwrite: the mirror has $site_only line(s) not in the canonical."
  echo "These may be edits that belong upstream. Review the diff:"
  echo
  printf '%s\n' "$d"
  echo
  echo "If those lines are stale/unwanted, re-run with: --apply --force"
  exit 1
fi

cp "$CANONICAL_BIB" "$SITE_BIB"
echo "updated mirror: copied $CANONICAL_BIB -> $SITE_BIB"
echo "next: re-run the generator to rebuild the (untracked) HTML, then commit data/vita.bib."
