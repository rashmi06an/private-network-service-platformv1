#!/usr/bin/env bash
# Task C — verify both backends respond directly on the LAN.
# Usage: ./test-backends.sh <MAC3_IP> <MAC4_IP>
set -euo pipefail

MAC3_IP="${1:-MAC3_IP_HERE}"
MAC4_IP="${2:-MAC4_IP_HERE}"

echo "== Backend A (Mac 3 :3001) =="
curl -i "http://${MAC3_IP}:3001/api/status"
echo; echo

echo "== Backend B (Mac 4 :3002) =="
curl -i "http://${MAC4_IP}:3002/api/status"
echo

echo "Expected: JSON { backend, status:\"ok\" } and an X-Backend: A / B header from each."
