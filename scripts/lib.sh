#!/usr/bin/env bash
# Shared Phase 2 addresses. All network checks keep TLS verification enabled.
set -euo pipefail
TEAM_PRIMARY_DNS=10.7.27.145
TEAM_BACKUP_DNS=10.7.27.247
TEAM_EDGE_IP=10.7.25.25
TEAM_BACKEND_A_IP=10.7.28.78
TEAM_BACKEND_B_IP=10.7.27.247
TEAM_URL="${TEAM_URL:-https://app.team1.test:8443}"
TEAM_CURL="${TEAM_CURL:-/usr/bin/curl}"
die() { printf 'FAIL: %s\n' "$*" >&2; exit 1; }
need() { command -v "$1" >/dev/null 2>&1 || die "Missing command: $1"; }
header() { awk -F': *' -v name="$2" 'tolower($1)==tolower(name){sub(/\r$/, "", $2); print $2}' "$1" | tail -1; }
fetch() {
    local url=$1 headers=$2
    shift 2
    local args=(--noproxy '*' --connect-timeout 3 --max-time 10 -sS -D "$headers" -o /dev/null -w '%{http_code}')
    if [ -n "${TEAM_CA_CERT:-}" ]; then args+=(--cacert "$TEAM_CA_CERT"); fi
    "$TEAM_CURL" "${args[@]}" "$@" "$url"
}
expect_code() { [ "$1" = "$2" ] || die "Expected HTTP $2, got $1"; }
dns_answer() {
    local server=$1 name=$2 expected=$3
    local answer
    answer=$(dig "@$server" "$name" A +time=2 +tries=1 +noall +answer) || die "$server did not answer $name"
    printf '%s\n' "$answer"
    printf '%s\n' "$answer" | awk -v name="$name." -v ip="$expected" '$1==name && $2==30 && $3=="IN" && $4=="A" && $5==ip {ok=1} END{exit !ok}' || die "$server: $name must resolve to $expected with TTL 30"
}
