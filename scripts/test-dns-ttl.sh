#!/usr/bin/env bash
set -euo pipefail
source "$(dirname "$0")/lib.sh"
for server in "$TEAM_PRIMARY_DNS" "$TEAM_BACKUP_DNS"; do
 answer=$(dig "@$server" ttl.team1.test A +time=2 +tries=1 +noall +answer)
 printf '%s server=%s\n%s\n' "$(date -u '+%Y-%m-%dT%H:%M:%SZ')" "$server" "$answer"
 printf '%s\n' "$answer" | awk '$1=="ttl.team1.test." && $2==30 && $4=="A" {ok=1} END{exit !ok}' || die "$server does not serve a 30-second TTL"
done
echo 'PASS: authoritative TTL configuration only.'
echo 'Direct repeated queries to these configured-record servers return a fresh TTL of 30.'
echo 'Expiry and manual-flush evidence must be collected separately using docs/ttl-experiments.md.'
