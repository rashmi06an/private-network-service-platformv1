#!/usr/bin/env bash
# Phase 2 / Extension D — HA failover behaviour.
# Sends repeated requests and prints X-Backend so you can watch the edge
# route around a stopped backend and rebalance when it recovers.
# Run from a client Mac.
set -euo pipefail

URL="${1:-https://app.team1.test:8443/api/status}"
COUNT="${2:-10}"

echo "== $COUNT requests to $URL =="
for i in $(seq 1 "$COUNT"); do
    out=$(curl -s -D - "$URL" -o /dev/null)
    code=$(printf '%s' "$out" | sed -n '1s/.* \([0-9][0-9][0-9]\).*/\1/p')
    backend=$(printf '%s' "$out" | awk -F': ' 'tolower($1)=="x-backend"{print $2}' | tr -d '\r')
    printf "request %2d -> HTTP %s  X-Backend: %s\n" "$i" "${code:-?}" "${backend:-<none>}"
    sleep 0.3
done

cat <<'EOF'

Demo sequence:
  - Both backends up  -> X-Backend alternates A / B.
  - Stop Backend A on Mac 3 (Ctrl-C) and re-run -> all responses X-Backend: B,
    HTTP stays 200 (edge fails over; no 502 to the client).
  - Restart Backend A -> within fail_timeout, A rejoins and A/B alternate again.

Single point of failure: the edge nginx on Mac 2 is still a SPOF. Eliminating it
would need a second edge + a floating/virtual IP or DNS failover (see Extension E).
EOF
