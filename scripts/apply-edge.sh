#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
source scripts/lib.sh
role="${1:?Usage: apply-edge.sh primary|standby}"
case "$role" in
 primary) expected=$TEAM_EDGE_IP; config=edge/nginx-phase2.conf.example;;
 standby) expected=$TEAM_BACKEND_A_IP; config=edge/standby-nginx.conf.example;;
 *) die 'Use primary or standby';;
esac
[ "$(ipconfig getifaddr en0)" = "$expected" ] || die "Wrong Mac/IP for $role"
need nginx
for file in app.team1.test.pem app.team1.test-key.pem; do
 sudo test -s "/opt/homebrew/etc/nginx/certs/$file" || die "Missing $file; follow edge/tls-setup-notes.md first"
done
state=".local-state/edge-$role-$(date -u '+%Y%m%dT%H%M%SZ')"
mkdir -p "$state"; chmod 700 .local-state "$state"
for file in nginx.conf tls.conf; do
 if [ -f "/opt/homebrew/etc/nginx/$file" ]; then sudo cp -p "/opt/homebrew/etc/nginx/$file" "$state/$file"; fi
done
# Validate a candidate with absolute include paths before replacing nginx.conf.
sed -e 's@include mime.types;@include /opt/homebrew/etc/nginx/mime.types;@' \
 -e "s@include /opt/homebrew/etc/nginx/tls.conf;@include $PWD/edge/tls.conf.example;@" "$config" > "$state/candidate.conf"
sudo nginx -t -c "$PWD/$state/candidate.conf"
sudo install -m 644 edge/tls.conf.example /opt/homebrew/etc/nginx/tls.conf
sudo install -m 644 "$config" /opt/homebrew/etc/nginx/nginx.conf
if ! sudo nginx -t; then
 for file in nginx.conf tls.conf; do if [ -f "$state/$file" ]; then sudo cp -p "$state/$file" "/opt/homebrew/etc/nginx/$file"; fi; done
 die "Validation failed; original config files restored from $state"
fi
if sudo test -s /opt/homebrew/var/run/nginx.pid && sudo kill -0 "$(sudo cat /opt/homebrew/var/run/nginx.pid)" 2>/dev/null; then
 sudo nginx -s reload
else
 sudo nginx
fi
echo "PASS: $role config applied. Original configs: $state"
echo 'Now run the trusted HTTPS and load-balancing checks; applying a config is not live proof.'
