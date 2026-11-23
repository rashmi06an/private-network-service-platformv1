#!/usr/bin/env bash
set -euo pipefail
source "$(dirname "$0")/lib.sh"
base="${1:-$TEAM_URL}"
tmp=$(mktemp -d); trap 'rm -rf "$tmp"' EXIT
code=$(fetch "${base%/}/api/status" "$tmp/status")
cat "$tmp/status"; expect_code "$code" 200
[ -n "$(header "$tmp/status" X-Backend)" ] || die 'Missing X-Backend'
[ -n "$(header "$tmp/status" X-Edge)" ] || die 'Missing X-Edge: apply corrected nginx config'
[ "$(header "$tmp/status" Cache-Control)" = no-store ] || die 'Status is missing no-store: check for an old backend process'
url="${base%/}/api/cache-demo"
code=$(fetch "$url" "$tmp/initial")
cat "$tmp/initial"; expect_code "$code" 200
etag=$(header "$tmp/initial" ETag)
[ -n "$etag" ] || die 'cache-demo returned no ETag'
[ "$etag" = '"team1-cache-v2"' ] || die 'cache-demo returned an old or unexpected validator: verify both deployed backends'
[[ "$(header "$tmp/initial" Cache-Control)" == *max-age=60* ]] || die 'Missing max-age=60'
code=$(fetch "$url" "$tmp/conditional" -H "If-None-Match: $etag")
cat "$tmp/conditional"; expect_code "$code" 304
[ "$(header "$tmp/conditional" ETag)" = "$etag" ] || die 'Validator changed on 304'
echo 'PASS: trusted by-name HTTPS, edge/backend headers, cache headers and conditional 304'
