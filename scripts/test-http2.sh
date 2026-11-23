#!/usr/bin/env bash
set -euo pipefail
source "$(dirname "$0")/lib.sh"
tmp=$(mktemp -d); trap 'rm -rf "$tmp"' EXIT
args=(--noproxy '*' --connect-timeout 10 --max-time 20 --http2 -sS -D "$tmp/headers" -o /dev/null -w '%{http_code} %{http_version}')
if [ -n "${TEAM_CA_CERT:-}" ]; then args+=(--cacert "$TEAM_CA_CERT"); fi
result=$("$TEAM_CURL" "${args[@]}" "$TEAM_URL/api/status")
cat "$tmp/headers"; printf 'HTTP_CODE_AND_VERSION=%s\n' "$result"
case "$result" in '200 2'|'200 2.0') echo 'PASS: actual HTTP/2 negotiated';; *) die 'HTTP/2 was not negotiated (a fallback to 1.1 is not an HTTP/2 pass)';; esac
