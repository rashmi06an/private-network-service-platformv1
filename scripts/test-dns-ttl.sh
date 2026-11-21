#!/usr/bin/env bash
# Phase 2 / Extension B — DNS TTL and controlled record change.
# Shows the TTL counting down on repeated queries.
# Run from a client Mac.
set -euo pipefail

SERVER="${1:-10.7.27.145}"     # Mac 1 primary DNS (Phase 2 IP)
DOMAIN="${2:-ttl.team1.test}"  # dedicated 30s-TTL demo record

echo "== TTL countdown for $DOMAIN via $SERVER =="
echo "(query 3 times, 5s apart — the TTL field should decrease)"
for i in 1 2 3; do
    printf "query %d: " "$i"
    dig +noall +answer "@$SERVER" "$DOMAIN"
    [ "$i" -lt 3 ] && sleep 5
done

cat <<'EOF'

Controlled record change (do this live on Mac 1):
  1. dig app.team1.test                          # note current IP + TTL (30)
  2. edit dnsmasq.conf: change the address= line to a different IP
  3. sudo brew services restart dnsmasq          # authoritative server now serves NEW ip
  4. dig app.team1.test                          # dig bypasses cache -> shows NEW ip immediately
  5. dscacheutil -q host -a name app.team1.test  # system cache -> may still show OLD ip
     ...until the 30s TTL expires, OR flush it:
  6. sudo dscacheutil -flushcache; sudo killall -HUP mDNSResponder   # immediate switch

This is exactly how DNS-based service migration / traffic cutover works in production.
EOF
