#!/usr/bin/env bash
set -euo pipefail
source "$(dirname "$0")/lib.sh"
url="${1:-$TEAM_URL/api/status}"; count="${2:-12}"
[[ "$count" =~ ^[0-9]+$ ]] && [ "$count" -ge 2 ] || die 'Count must be at least 2'
tmp=$(mktemp -d); trap 'rm -rf "$tmp"' EXIT
a=0;b=0
for ((i=1;i<=count;i++)); do
 code=$(fetch "$url" "$tmp/headers"); expect_code "$code" 200
 backend=$(header "$tmp/headers" X-Backend)
 case "$backend" in A) a=$((a+1));; B) b=$((b+1));; *) die "Missing/invalid X-Backend: $backend";; esac
 printf 'request=%s HTTP=%s X-Backend=%s\n' "$i" "$code" "$backend"
done
[ "$a" -gt 0 ] && [ "$b" -gt 0 ] || die "Did not observe both backends: A=$a B=$b"
printf 'PASS: A=%s B=%s (other concurrent traffic can affect strict alternation)\n' "$a" "$b"
