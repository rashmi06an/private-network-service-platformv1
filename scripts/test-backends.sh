#!/usr/bin/env bash
set -euo pipefail
source "$(dirname "$0")/lib.sh"
a="${1:-$TEAM_BACKEND_A_IP}"; b="${2:-$TEAM_BACKEND_B_IP}"
tmp=$(mktemp -d); trap 'rm -rf "$tmp"' EXIT
for pair in "A $a 3001" "B $b 3002"; do
 set -- $pair
 base="http://$2:$3"
 code=$(fetch "$base/api/status" "$tmp/headers")
 cat "$tmp/headers"
 expect_code "$code" 200
 [ "$(header "$tmp/headers" X-Backend)" = "$1" ] || die "Wrong backend identity for $2:$3"
 [ "$(header "$tmp/headers" Cache-Control)" = no-store ] || die "Backend $1 is missing no-store; check whether old code is running"
 code=$(fetch "$base/api/cache-demo" "$tmp/cache")
 cat "$tmp/cache"; expect_code "$code" 200
 [ "$(header "$tmp/cache" X-Backend)" = "$1" ] || die "Wrong cache backend identity for $2:$3"
 [ "$(header "$tmp/cache" ETag)" = '"team1-cache-v2"' ] || die "Backend $1 is missing the shared team1-cache-v2 validator; check deployed source"
 [ "$(header "$tmp/cache" Cache-Control)" = 'public, max-age=60' ] || die "Backend $1 cache policy differs"
 code=$(fetch "$base/api/cache-demo" "$tmp/conditional" -H 'If-None-Match: "team1-cache-v2"')
 cat "$tmp/conditional"; expect_code "$code" 304
 [ "$(header "$tmp/conditional" ETag)" = '"team1-cache-v2"' ] || die "Backend $1 validator changed on conditional request"
done
echo 'PASS: both updated backends have correct identities, no-store, shared cache validator and conditional 304'
