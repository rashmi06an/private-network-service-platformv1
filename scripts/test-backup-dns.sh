#!/usr/bin/env bash
set -euo pipefail
source "$(dirname "$0")/lib.sh"
mode="${1:-both-up}"
case "$mode" in
 both-up)
  for server in "$TEAM_PRIMARY_DNS" "$TEAM_BACKUP_DNS"; do
   for name in app.team1.test api.team1.test ttl.team1.test; do dns_answer "$server" "$name" "$TEAM_EDGE_IP"; done
  done;;
 primary-down)
  if dig "@$TEAM_PRIMARY_DNS" app.team1.test +time=2 +tries=1 > /dev/null 2>&1; then die 'Primary still answers: do not claim primary-down failover'; fi
  for name in app.team1.test api.team1.test ttl.team1.test; do dns_answer "$TEAM_BACKUP_DNS" "$name" "$TEAM_EDGE_IP"; done
  echo 'System lookup (flush system cache before invoking this stage):'
  lookup=$(dscacheutil -q host -a name app.team1.test); printf '%s\n' "$lookup"
  printf '%s\n' "$lookup" | awk -v ip="$TEAM_EDGE_IP" '$1=="ip_address:" && $2==ip {ok=1} END{exit !ok}' || die 'System lookup did not return the primary edge'
  tmp=$(mktemp -d); trap 'rm -rf "$tmp"' EXIT
  code=$(fetch "$TEAM_URL/api/status" "$tmp/headers"); cat "$tmp/headers"; expect_code "$code" 200
  ;;
 *) die 'Usage: test-backup-dns.sh both-up|primary-down';;
esac
echo "PASS: $mode (keep backup query receipt and primary-stop timeline as supporting evidence)"
