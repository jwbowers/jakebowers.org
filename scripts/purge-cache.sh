#!/bin/bash
# Purge a Cloudflare-cached URL for static.jakebowers.org
#
# Usage:
#   ./scripts/purge-cache.sh https://static.jakebowers.org/MISC/ps531s26_causal.pdf
#   ./scripts/purge-cache.sh MISC/ps531s26_causal.pdf
#
# Requires CLOUDFLARE_PURGE_TOKEN environment variable.
# Create one at: https://dash.cloudflare.com/profile/api-tokens
# (Zone > Cache Purge > Purge permission for jakebowers.org)

set -euo pipefail

ZONE_ID="00d57633940d082931a9137e7185e73a"
BASE_URL="https://static.jakebowers.org"

if [ -z "${CLOUDFLARE_PURGE_TOKEN:-}" ]; then
  echo "Error: Set CLOUDFLARE_PURGE_TOKEN in your environment." >&2
  echo "  export CLOUDFLARE_PURGE_TOKEN=your_token_here" >&2
  exit 1
fi

if [ $# -eq 0 ]; then
  echo "Usage: $0 <url-or-path> [url-or-path ...]" >&2
  echo "  e.g. $0 MISC/ps531s26_causal.pdf" >&2
  echo "  e.g. $0 https://static.jakebowers.org/MISC/bowers-vita.pdf" >&2
  exit 1
fi

# Build JSON array of full URLs
urls=""
for arg in "$@"; do
  if [[ "$arg" == https://* ]]; then
    url="$arg"
  else
    url="${BASE_URL}/${arg}"
  fi
  if [ -z "$urls" ]; then
    urls="\"${url}\""
  else
    urls="${urls}, \"${url}\""
  fi
done

response=$(curl -s -X POST \
  "https://api.cloudflare.com/client/v4/zones/${ZONE_ID}/purge_cache" \
  -H "Authorization: Bearer ${CLOUDFLARE_PURGE_TOKEN}" \
  -H "Content-Type: application/json" \
  --data "{\"files\":[${urls}]}")

if echo "$response" | python3 -c "import sys,json; sys.exit(0 if json.load(sys.stdin)['success'] else 1)" 2>/dev/null; then
  echo "Cache purged for:"
  for arg in "$@"; do
    if [[ "$arg" == https://* ]]; then
      echo "  $arg"
    else
      echo "  ${BASE_URL}/${arg}"
    fi
  done
else
  echo "Purge failed:" >&2
  echo "$response" >&2
  exit 1
fi
