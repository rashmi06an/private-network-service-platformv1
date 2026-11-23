#!/usr/bin/env bash
set -euo pipefail
source "$(dirname "$0")/lib.sh"
mode="${1:-balanced}"; url="${2:-$TEAM_URL/api/status}"; count="${3:-12}"
case "$mode" in balanced|a-down|recovered) ;; *) die 'Usage: test-ha-failover.sh balanced|a-down|recovered [URL] [COUNT]';; esac
[[ "$count" =~ ^[0-9]+$ ]] && [ "$count" -ge 2 ] || die 'Count must be at least 2'
tmp=$(mktemp -d); trap 'rm -rf "$tmp"' EXIT
a=0;b=0
for ((i=1;i<=count;i++)); do
 code=$(fetch "$url" "$tmp/headers"); expect_code "$code" 200
 backend=$(header "$tmp/headers" X-Backend)
 case "$backend" in A) a=$((a+1));; B) b=$((b+1));; *) die "Invalid backend: $backend";; esac
 [ "$mode" != a-down ] || [ "$backend" = B ] || die 'A-down stage returned a response from A'
 printf 'stage=%s request=%s HTTP=%s X-Backend=%s\n' "$mode" "$i" "$code" "$backend"
 sleep 0.3
done
if [ "$mode" = a-down ]; then [ "$a" = 0 ] && [ "$b" = "$count" ] || die 'A-down result failed';
else [ "$a" -gt 0 ] && [ "$b" -gt 0 ] || die "Both backends not observed: A=$a B=$b"; fi
echo "PASS: $mode A=$a B=$b"
