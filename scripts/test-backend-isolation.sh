#!/usr/bin/env bash
set -euo pipefail
source "$(dirname "$0")/lib.sh"
mode="${1:-isolated}"
case "$mode" in isolated|restored) ;; *) die 'Use isolated or restored';; esac
actual=$(ipconfig getifaddr en0)
[ "$actual" = "$TEAM_PRIMARY_DNS" ] || die 'Run this denial/rollback test from Mac 1 (not an edge or backend)'
tmp=$(mktemp -d); trap 'rm -rf "$tmp"' EXIT
for pair in "A $TEAM_BACKEND_A_IP 3001" "B $TEAM_BACKEND_B_IP 3002"; do
 set -- $pair
 if code=$(fetch "http://$2:$3/api/status" "$tmp/headers"); then
  [ "$mode" = restored ] || die "Backend $1 is directly reachable; isolation is not active"
  expect_code "$code" 200
  [ "$(header "$tmp/headers" X-Backend)" = "$1" ] || die 'Wrong restored backend'
  echo "RESTORED: backend $1 HTTP=$code"
 else
  [ "$mode" = isolated ] || die "Backend $1 still inaccessible after rollback"
  echo "DENIED: backend $1; pair this with a contemporaneous positive test from Mac 2"
 fi
done
code=$(fetch "$TEAM_URL/api/status" "$tmp/edge"); cat "$tmp/edge"; expect_code "$code" 200
echo "PASS: $mode; by-name HTTPS via edge remains available"
