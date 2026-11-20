#!/usr/bin/env bash
# Safe, non-destructive verification on a client Mac; no root required.
# Does NOT claim to verify intentional failures or before/after cache flushing.
set -u
DNS_PRIMARY="${DNS_PRIMARY:-10.7.27.145}"
DNS_BACKUP="${DNS_BACKUP:-10.7.27.247}"
EDGE="${EDGE:-10.7.25.25}"
BACKEND_A="${BACKEND_A:-10.7.28.78:3001}"
BACKEND_B="${BACKEND_B:-10.7.27.247:3002}"
OUT="${1:-$HOME/team1-phase2-final-check-$(date +%Y%m%d-%H%M%S).txt}"
PASS=0; FAIL=0
check() {
  local label="$1" actual="$2" expected="$3"
  if [[ "$actual" == *"$expected"* ]]; then
    echo "PASS $label: $actual"; PASS=$((PASS + 1))
  else
    echo "FAIL $label: got '$actual' (expected to include '$expected')"; FAIL=$((FAIL + 1))
  fi
}
{
  echo "=== CN Team 1 Phase 2 baseline (non-destructive) ==="
  date
  echo "Current en0 IPv4: $(ipconfig getifaddr en0 2>/dev/null || echo unavailable)"
  P=$(dig @"$DNS_PRIMARY" app.team1.test +short +time=2 +tries=1 2>/dev/null)
  B=$(dig @"$DNS_BACKUP" app.team1.test +short +time=2 +tries=1 2>/dev/null)
  check 'Primary DNS' "$P" "$EDGE"
  check 'Backup DNS' "$B" "$EDGE"
  A_BODY=$(/usr/bin/curl --noproxy '*' --connect-timeout 3 --max-time 5 -fsS "http://$BACKEND_A/api/status" 2>/dev/null || true)
  B_BODY=$(/usr/bin/curl --noproxy '*' --connect-timeout 3 --max-time 5 -fsS "http://$BACKEND_B/api/status" 2>/dev/null || true)
  check 'Backend A' "$A_BODY" '"backend":"A"'
  check 'Backend B' "$B_BODY" '"backend":"B"'
  HTTPS=$(/usr/bin/curl --noproxy '*' --connect-timeout 5 --max-time 10 -sS -D - -o /dev/null https://app.team1.test:8443/api/status 2>&1)
  check 'Trusted HTTPS 200' "$HTTPS" '200 OK'
  check 'HTTPS backend header' "$HTTPS" 'X-Backend:'
  echo '--- HTTPS response headers ---'
  printf '%s\n' "$HTTPS"
  echo "SUMMARY: $PASS PASS / $FAIL FAIL"
} 2>&1 | tee "$OUT"
echo "Evidence file: $OUT"
if [[ "$(grep -c '^FAIL ' "$OUT")" -gt 0 ]]; then exit 1; fi
