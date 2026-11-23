#!/usr/bin/env bash
set -euo pipefail
source "$(dirname "$0")/lib.sh"
server="${1:-$TEAM_PRIMARY_DNS}"
for name in app.team1.test api.team1.test ttl.team1.test; do dns_answer "$server" "$name" "$TEAM_EDGE_IP"; done
echo "PASS: all three normal-state records resolve through $server"
echo 'Scoped macOS DNS is checked separately with dscacheutil/scutil; bare dig ignores it.'
