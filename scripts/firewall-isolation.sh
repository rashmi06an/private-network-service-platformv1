#!/usr/bin/env bash
# Owns one reachable project anchor and one PF enable reference; no global flush.
set -euo pipefail
cd "$(dirname "$0")/.."
source scripts/lib.sh
action="${1:-show}"; edges="${2:-primary}"
anchor=com.apple/team1_submission
state=.local-state/pf-isolation
actual=$(ipconfig getifaddr en0)
case "$actual" in "$TEAM_BACKEND_A_IP") port=3001;; "$TEAM_BACKEND_B_IP") port=3002;; *) die 'Run only on Backend A or B';; esac
mkdir -p "$state"; chmod 700 .local-state "$state"
make_rules() {
 case "$edges" in primary) sources="$TEAM_EDGE_IP";; both) sources="{ $TEAM_EDGE_IP $TEAM_BACKEND_A_IP }";; *) die 'Edges must be primary or both';; esac
 printf 'pass in quick on en0 inet proto tcp from %s to %s port %s\nblock drop in quick on en0 inet proto tcp from any to %s port %s\n' "$sources" "$actual" "$port" "$actual" "$port" > "$state/rules.pf"
 sudo pfctl -nf "$state/rules.pf"
}
case "$action" in
 apply)
  [ ! -f "$state/active-token" ] || die 'Project anchor already active; use show, set-edges or rollback'
  sudo pfctl -sr > "$state/main-before.txt"
  grep -F 'anchor "com.apple/*"' "$state/main-before.txt" >/dev/null || die 'Required parent anchor call missing; do not load a detached anchor'
  existing=$(sudo pfctl -a "$anchor" -sr 2>/dev/null)
  [ -z "$existing" ] || die 'Project anchor contains pre-existing rules; inspect before changing'
  sudo cp -p /etc/pf.conf "$state/pf.conf.before"
  make_rules
  sudo pfctl -a "$anchor" -f "$state/rules.pf"
  if ! sudo pfctl -E > "$state/enable-output.txt" 2>&1; then sudo pfctl -a "$anchor" -F rules; cat "$state/enable-output.txt"; die 'PF enable failed; project rules cleared'; fi
  token=$(sed -n 's/.*Token[[:space:]]*:[[:space:]]*\([0-9][0-9]*\).*/\1/p' "$state/enable-output.txt")
  [ -n "$token" ] || die 'Enable token missing; preserve enable-output.txt and inspect before cleanup'
  printf '%s\n' "$token" > "$state/active-token"
  printf 'ACTIVE_UTC=%s edges=%s host=%s port=%s\n' "$(date -u '+%Y-%m-%dT%H:%M:%SZ')" "$edges" "$actual" "$port"
  ;;
 set-edges)
  [ -f "$state/active-token" ] || die 'No project-owned active ruleset'
  make_rules
  sudo pfctl -a "$anchor" -f "$state/rules.pf";;
 rollback)
  [ -f "$state/active-token" ] || die 'No project-owned active token; do not disable PF globally'
  token=$(cat "$state/active-token")
  [[ "$token" =~ ^[0-9]+$ ]] || die 'Invalid saved PF token'
  sudo pfctl -a "$anchor" -F rules
  sudo pfctl -X "$token"
  mv "$state/active-token" "$state/released-token-$(date -u '+%Y%m%dT%H%M%SZ')"
  echo 'ROLLED BACK: project rules cleared; only the project enable reference released';;
 show) ;;
 *) die 'Usage: firewall-isolation.sh apply [primary|both] | set-edges primary|both | rollback | show';;
esac
sudo pfctl -a "$anchor" -vvsr
sudo pfctl -s info | head -5
