#!/usr/bin/env bash
# Run on the selected DNS Mac; backs up files and refuses an unknown port-53 process.
set -euo pipefail
cd "$(dirname "$0")/.."
source scripts/lib.sh
role="${1:?Use primary on Mac 1 or backup on Mac 4}"
case "$role" in
 primary) expected=$TEAM_PRIMARY_DNS; config=dns/dnsmasq-phase2.conf.example;;
 backup) expected=$TEAM_BACKUP_DNS; config=dns/backup-dnsmasq.conf.example;;
 *) die 'Use primary or backup';;
esac
[ "$(ipconfig getifaddr en0)" = "$expected" ] || die "Wrong Mac/IP for $role"
need brew
binary="$(brew --prefix dnsmasq)/sbin/dnsmasq"
[ -x "$binary" ] || die 'Install dnsmasq with brew install dnsmasq'
backup=".local-state/dns-before-$(date -u '+%Y%m%dT%H%M%SZ')"
mkdir -p "$backup"; chmod 700 .local-state "$backup"
for file in dnsmasq.conf team1-project.hosts; do
 if [ -f "/opt/homebrew/etc/$file" ]; then sudo cp -p "/opt/homebrew/etc/$file" "$backup/$file"; fi
done
sudo brew services stop dnsmasq
listeners=$(sudo lsof -t -nP -iUDP:53 -iTCP:53 2>/dev/null | sort -u || true)
[ -z "$listeners" ] || die "Port 53 still belongs to PID(s) $listeners. Stop the identified old manual DNS instance first; this script will not kill it automatically. Backups: $backup"
sudo install -m 644 dns/project.hosts /opt/homebrew/etc/team1-project.hosts
sudo install -m 644 "$config" /opt/homebrew/etc/dnsmasq.conf
if ! sudo "$binary" --test --conf-file=/opt/homebrew/etc/dnsmasq.conf; then
 if [ -f "$backup/dnsmasq.conf" ]; then sudo cp -p "$backup/dnsmasq.conf" /opt/homebrew/etc/dnsmasq.conf; fi
 if [ -f "$backup/team1-project.hosts" ]; then sudo cp -p "$backup/team1-project.hosts" /opt/homebrew/etc/team1-project.hosts; fi
 die "Syntax check failed; original files restored. Review $backup before restarting."
fi
sudo brew services start dnsmasq
sleep 1
scripts/test-dns.sh "$expected"
echo "Saved pre-change files: $backup"
echo 'PASS: selected DNS config installed; verify the PID and both-resolver synchronization too'
