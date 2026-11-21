#!/usr/bin/env bash
# Phase 2 / Extension C — service isolation (backend firewall).
# Run from a CLIENT Mac (NOT the edge). Proves direct access to the backend
# ports is blocked, while the service still works through the edge by name.
set -euo pipefail

MAC3_IP="${1:-10.7.28.78}"   # Backend A
MAC4_IP="${2:-10.7.27.247}"   # Backend B

echo "== Direct backend access from this client (expected: BLOCKED) =="
for pair in "A ${MAC3_IP} 3001" "B ${MAC4_IP} 3002"; do
    set -- $pair
    name=$1 ip=$2 port=$3
    printf -- "-> Backend %s  %s:%s ... " "$name" "$ip" "$port"
    if curl -s --max-time 5 -o /dev/null "http://${ip}:${port}/api/status"; then
        echo "REACHABLE (isolation NOT active)"
    else
        echo "blocked / timed out (isolation active)"
    fi
done

echo
echo "== Service through the edge by name (expected: WORKS) =="
curl -s -o /dev/null -w "https://app.team1.test:8443/api/status -> HTTP %{http_code}\n" \
    https://app.team1.test:8443/api/status

echo
echo "Note: from the EDGE (Mac 2) the same direct curl to :3001/:3002 still succeeds."
