#!/usr/bin/env bash
# Task D — prove round-robin load balancing across Backend A and B.
# Sends repeated requests and prints the X-Backend header each time.
set -euo pipefail

URL="${1:-https://app.team1.test/api/status}"
COUNT="${2:-8}"

echo "== Load balancing test: $COUNT requests to $URL =="
for i in $(seq 1 "$COUNT"); do
    backend=$(curl -s -D - "$URL" -o /dev/null | awk -F': ' 'tolower($1)=="x-backend"{print $2}' | tr -d '\r')
    printf "request %2d -> X-Backend: %s\n" "$i" "${backend:-<none>}"
done

echo
echo "Expected: responses alternate between A and B (round-robin)."
