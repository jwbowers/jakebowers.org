#!/usr/bin/env bash
#
# vita-bib-check-notify.sh -- run the vita.bib drift check and, if the mirror
# has drifted from the canonical (or the check errors), post a macOS
# notification and log the result. Meant to be invoked by a launchd agent on a
# weekly schedule (see ~/Library/LaunchAgents/org.jakebowers.vita-bib-check.plist).
#
# Read-only: it never modifies either bib file. macOS specific (uses osascript).

# No 'set -e': we want to capture a non-zero exit from the check, not abort on it.
script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
log="$HOME/Library/Logs/vita-bib-check.log"
ts="$(date '+%Y-%m-%d %H:%M:%S')"

out="$("$script_dir/sync-vita-bib.sh" 2>&1)"
status=$?

{
  echo "[$ts] exit=$status"
  echo "$out"
  echo "----"
} >> "$log"

if [ "$status" -ne 0 ]; then
  /usr/bin/osascript -e 'display notification "data/vita.bib has drifted from the canonical ~/repos/vita. Run bin/sync-vita-bib.sh." with title "vita.bib out of sync"' >/dev/null 2>&1 || true
fi

exit 0
