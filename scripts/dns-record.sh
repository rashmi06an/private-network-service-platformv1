#!/usr/bin/env bash
# A scheduled HUP makes a 30-second experiment practical on both DNS Macs.
set -euo pipefail
cd "$(dirname "$0")/.."
source scripts/lib.sh
name="${1:?Usage: dns-record.sh app|api|ttl IPv4 [unix-epoch]}"
ip="${2:?Missing target IPv4}"; epoch="${3:-0}"
case "$name" in app|api|ttl) ;; *) die 'Only the three project records may be changed';; esac
case "$ip" in "$TEAM_EDGE_IP"|"$TEAM_BACKEND_A_IP") ;; *) die 'Target must be primary or standby edge IP';; esac
[[ "$epoch" =~ ^[0-9]+$ ]] || die 'Epoch must be an integer'
actual=$(ipconfig getifaddr en0)
case "$actual" in "$TEAM_PRIMARY_DNS"|"$TEAM_BACKUP_DNS") ;; *) die 'Run on Mac 1 or Mac 4';; esac
file=/opt/homebrew/etc/team1-project.hosts
pidfile=/opt/homebrew/var/run/dnsmasq-team1.pid
[ -f "$file" ] && [ -f "$pidfile" ] || die 'First install the corrected DNS config using setup-dns.sh'
pid=$(sudo cat "$pidfile")
[[ "$pid" =~ ^[0-9]+$ ]] || die 'Invalid service PID'
process=$(ps -p "$pid" -o comm=)
[[ "$process" == *dnsmasq* ]] || die 'PID does not belong to dnsmasq'
sudo -v
if [ "$epoch" -gt 0 ]; then
 now=$(date +%s)
 [ "$epoch" -gt "$now" ] && [ "$((epoch-now))" -le 600 ] || die 'Choose an epoch in the next 10 minutes'
 printf 'ARMED: %s %s -> %s at UNIX_EPOCH=%s\n' "$actual" "$name.team1.test" "$ip" "$epoch"
 while [ "$(date +%s)" -lt "$epoch" ]; do sleep 1; done
fi
tmp=$(mktemp); trap 'rm -f "$tmp"' EXIT
awk -v host="$name.team1.test" -v ip="$ip" '($2==host){$1=ip;found=1} {print} END{if(!found)exit 1}' "$file" > "$tmp" || die 'Project record not found'
mkdir -p .local-state/dns-record-backups
sudo cp -p "$file" ".local-state/dns-record-backups/$(date -u '+%Y%m%dT%H%M%SZ')-$name.hosts"
sudo -n install -m 644 "$tmp" "$file"
sudo -n kill -HUP "$pid"
printf 'CHANGED_UTC=%s DNS=%s\n' "$(date -u '+%Y-%m-%dT%H:%M:%SZ')" "$actual"
dns_answer "$actual" "$name.team1.test" "$ip"
