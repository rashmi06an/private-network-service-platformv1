#!/usr/bin/env bash
# Phase 2 / Extension A — backup DNS resolver.
# Shows both the primary (Mac 1) and backup (Mac 4) resolve the project names.
# Run from a client Mac.
set -euo pipefail

PRIMARY="${1:-10.7.27.145}"   # Mac 1
BACKUP="${2:-10.7.27.247}"    # Mac 4
DOMAINS=("app.team1.test" "api.team1.test")

for d in "${DOMAINS[@]}"; do
    echo "=== $d ==="
    echo "--- primary resolver ($PRIMARY, Mac 1) ---"
    dig +noall +answer +stats "@$PRIMARY" "$d" | sed -n '1,3p'
    echo "--- backup resolver  ($BACKUP, Mac 4) ---"
    dig +noall +answer +stats "@$BACKUP" "$d" | sed -n '1,3p'
    echo
done

echo "Expected: both resolvers return 10.7.25.25 (Mac 2) with the same TTL."
echo "Failover: stop dnsmasq on Mac 1, then 'dig @$BACKUP app.team1.test' still answers,"
echo "          and 'dscacheutil -q host -a name app.team1.test' still resolves via the backup."
echo "Note: a bare 'dig app.team1.test' uses the global resolver (8.8.8.8) -> NXDOMAIN; always name the server."
