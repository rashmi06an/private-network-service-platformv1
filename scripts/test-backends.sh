#!/usr/bin/env bash
set -euo pipefail
source "$(dirname "$0")/lib.sh"
a="${1:-$TEAM_BACKEND_A_IP}"; b="${2:-$TEAM_BACKEND_B_IP}"
tmp=$(mktemp -d); trap 'rm -rf "$tmp"' EXIT
for pair in "A $a 3001" "B $b 3002"; do
 set -- $pair
 code=$(fetch "http://$2:$3/api/status" "$tmp/headers")
 cat "$tmp/headers"
 expect_code "$code" 200
 [ "$(header "$tmp/headers" X-Backend)" = "$1" ] || die "Wrong backend identity for $2:$3"
done
echo 'PASS: both direct backend endpoints returned 200 and the correct identity'
