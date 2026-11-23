#!/usr/bin/env bash
# A scheduled normal-hostname request from Mac1 during Mac2's cached-old window.
set -euo pipefail
cd "$(dirname "$0")/.."
source scripts/lib.sh
epoch="${1:?Usage: fresh-cutover-client.sh shared-epoch}"
[[ "$epoch" =~ ^[0-9]+$ ]] || die 'Epoch must be an integer'
[ "$(ipconfig getifaddr en0)" = "$TEAM_PRIMARY_DNS" ] || die 'Run the fresh comparison on Mac1'
now=$(date +%s)
[ "$now" -le "$((epoch+10))" ] && [ "$((epoch-now))" -le 600 ] || die 'Fresh-client window missed or schedule too far away'
sudo -v
printf 'FRESH_CLIENT_ARMED epoch=%s probe_epoch=%s\n' "$epoch" "$((epoch+5))"
while [ "$(date +%s)" -lt "$((epoch+5))" ]; do sleep 0.2; done
printf 'FRESH_CLIENT_START_UTC=%s\n' "$(date -u '+%Y-%m-%dT%H:%M:%SZ')"
sudo dscacheutil -flushcache
sudo killall -HUP mDNSResponder
lookup=$(dscacheutil -q host -a name app.team1.test); printf '%s\n' "$lookup"
printf '%s\n' "$lookup" | awk -v ip="$TEAM_BACKEND_A_IP" '$1=="ip_address:" && $2==ip{ok=1} END{exit !ok}' || die 'Fresh system lookup did not return standby'
tmp=$(mktemp -d); trap 'rm -rf "$tmp"' EXIT
result=$(/usr/bin/curl --noproxy '*' --connect-timeout 10 --max-time 20 -sS -D "$tmp/headers" -o /dev/null -w '%{http_code} %{remote_ip}' "$TEAM_URL/api/status")
cat "$tmp/headers"; printf 'FRESH_HTTP_AND_IP=%s\n' "$result"
[ "$result" = "200 $TEAM_BACKEND_A_IP" ] || die 'Fresh client did not connect successfully to standby'
[ "$(header "$tmp/headers" X-Edge)" = standby-mac3 ] || die 'Fresh client reached the wrong edge'
[ "$(date +%s)" -le "$((epoch+25))" ] || die 'Fresh result arrived outside the cached-old comparison window'
printf 'PASS: fresh by-name HTTPS reaches standby within the cached-old window; END_UTC=%s\n' "$(date -u '+%Y-%m-%dT%H:%M:%SZ')"
