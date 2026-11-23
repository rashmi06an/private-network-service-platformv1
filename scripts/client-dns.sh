#!/usr/bin/env bash
# Only the private .test zone changes; restores the exact prior scoped file.
set -euo pipefail
cd "$(dirname "$0")/.."
source scripts/lib.sh
mode="${1:-install}"
state=.local-state/client-dns
target=/etc/resolver/team1.test
mkdir -p "$state"; chmod 700 .local-state "$state"
case "$mode" in
 install)
  if [ ! -e "$state/snapshot-made" ]; then
   if [ -e "$target" ]; then sudo cp -p "$target" "$state/original"; else touch "$state/original-absent"; fi
   touch "$state/snapshot-made"
  fi
  tmp=$(mktemp); trap 'rm -f "$tmp"' EXIT
  printf 'nameserver %s\nnameserver %s\n' "$TEAM_PRIMARY_DNS" "$TEAM_BACKUP_DNS" > "$tmp"
  sudo mkdir -p /etc/resolver
  sudo install -m 644 "$tmp" "$target";;
 restore)
  [ -e "$state/snapshot-made" ] || die 'No saved resolver state'
  if [ -e "$state/original" ]; then sudo cp -p "$state/original" "$target";
  elif [ -e "$state/original-absent" ]; then sudo rm -f "$target"; fi;;
 *) die 'Usage: client-dns.sh install|restore';;
esac
sudo dscacheutil -flushcache
sudo killall -HUP mDNSResponder
if [ -f "$target" ]; then cat "$target"; fi
scutil --dns | sed -n '/domain *: team1.test/,+8p'
echo "PASS: scoped DNS $mode; normal internet resolver settings were not overwritten"
