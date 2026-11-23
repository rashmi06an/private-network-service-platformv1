#!/usr/bin/env bash
# Deliberately misconfigure only this client's project-zone resolver, then restore.
set -euo pipefail
cd "$(dirname "$0")/.."
source scripts/lib.sh
actual=$(ipconfig getifaddr en0)
case "$actual" in "$TEAM_EDGE_IP"|"$TEAM_BACKEND_A_IP") ;; *) die 'Run this client-only rehearsal on Mac 2 or Mac 3';; esac
state=".local-state/wrong-dns-$(date -u '+%Y%m%dT%H%M%SZ')"
mkdir -p "$state"; chmod 700 .local-state "$state"
target=/etc/resolver/team1.test
if [ -e "$target" ]; then sudo cp -p "$target" "$state/original"; else touch "$state/original-absent"; fi
# A LAN address on normal DNS port53 is honored by current macOS scoped DNS.
# Refuse any existing DNS listener; never redirect to or stop an unrelated service.
sudo -v
if sudo lsof -nP "-iUDP@$actual:53" "-iTCP@$actual:53"; then
 die 'This client already has a port53 socket; finish other DNS experiments first'
fi
scripts/test-https.sh
changed=0
restore() {
 if [ "$changed" = 1 ]; then
  if [ -e "$state/original" ]; then sudo cp -p "$state/original" "$target"; else sudo rm -f "$target"; fi
  sudo dscacheutil -flushcache
  sudo killall -HUP mDNSResponder
  echo 'RESTORED: prior scoped client DNS file'
 fi
}
trap restore EXIT
printf 'nameserver %s\ntimeout 1\n' "$actual" > "$state/wrong.resolver"
changed=1
sudo install -m 644 "$state/wrong.resolver" "$target"
sudo dscacheutil -flushcache; sudo killall -HUP mDNSResponder
echo 'INTENTIONAL WRONG EFFECTIVE CLIENT DNS:'; cat "$target"
scutil --dns | sed -n '/domain *: team1.test/,+8p'
ping -c 2 -W 2000 "$TEAM_EDGE_IP"
set +e
"$TEAM_CURL" --noproxy '*' --connect-timeout 3 --max-time 8 -sS "$TEAM_URL/api/status" > "$state/unexpected-response.txt" 2> "$state/curl-error.txt"
rc=$?
set -e
cat "$state/curl-error.txt"
if [ "$rc" = 0 ]; then
 die 'Hostname request unexpectedly succeeded: investigate other resolvers/caches; this is not a valid failure exhibit'
fi
case "$rc" in 6|28) ;; *) die "Failure was not a DNS-resolution error (curl exit$rc)";; esac
grep -Eq 'Could not resolve|Resolving timed out' "$state/curl-error.txt" || die 'Curl did not report a resolution failure'
echo 'OBSERVED: normal hostname request fails while direct edge IP remains reachable'
restore; changed=0
scripts/test-https.sh
echo 'PASS: deliberate client-DNS fault and restored end-to-end service'
