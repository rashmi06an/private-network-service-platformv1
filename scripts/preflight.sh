#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
source scripts/lib.sh
role="${1:?Usage: scripts/preflight.sh mac1|mac2|mac3|mac4}"
case "$role" in
 mac1) expected=$TEAM_PRIMARY_DNS;; mac2) expected=$TEAM_EDGE_IP;;
 mac3) expected=$TEAM_BACKEND_A_IP;; mac4) expected=$TEAM_BACKEND_B_IP;;
 *) die 'Role must be mac1, mac2, mac3, or mac4';;
esac
printf 'ROLE=%s UTC=%s\n' "$role" "$(date -u '+%Y-%m-%dT%H:%M:%SZ')"
actual=$(ipconfig getifaddr en0) || die 'Cannot read en0 address'
printf 'IP=%s EXPECTED=%s\n' "$actual" "$expected"
[ "$actual" = "$expected" ] || die 'IP changed; update inventory/configs before experiments'
ifconfig en0 | awk '/ether |inet |status:/{print}'
route -n get default | awk '/gateway:|interface:/{print}'
printf '\nEffective private resolver settings:\n'
if [ -f /etc/resolver/team1.test ]; then cat /etc/resolver/team1.test; else echo 'No /etc/resolver/team1.test'; fi
scutil --dns | sed -n '/domain *: team1.test/,+8p'
failed=0
for ip in "$TEAM_PRIMARY_DNS" "$TEAM_EDGE_IP" "$TEAM_BACKEND_A_IP" "$TEAM_BACKEND_B_IP"; do
 [ "$ip" = "$actual" ] && continue
 printf '\nPING %s -> %s\n' "$actual" "$ip"
 ping -c 2 -W 2000 "$ip" || failed=1
done
printf '\nProject listeners on this Mac:\n'
lsof -nP -iTCP:8443 -iTCP:3001 -iTCP:3002 -sTCP:LISTEN || true
printf '\nTool versions:\n'
python3 --version
"$TEAM_CURL" --version | head -1
[ "$failed" = 0 ] || die 'One or more pairwise ping checks failed; inspect LAN/ICMP policy'
echo 'PASS: inventory and all three outbound ping checks'
