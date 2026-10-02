#!/usr/bin/env bash
# Task C — verify both backends respond directly on the LAN.
# Usage: ./test-backends.sh <MAC3_IP> <MAC4_IP>
set -euo pipefail

MAC3_IP="${1:-10.7.21.15}"
MAC4_IP="${2:-10.7.23.47}"

echo "== Backend A (Mac 3 :3001) =="
curl -i "http://${MAC3_IP}:3001/api/status"
echo; echo

echo "== Backend B (Mac 4 :3002) =="
curl -i "http://${MAC4_IP}:3002/api/status"
echo

echo "Expected: JSON { backend, status:\"ok\" } and an X-Backend: A / B header from each."
