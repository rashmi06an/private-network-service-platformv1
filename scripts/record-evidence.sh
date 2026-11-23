#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
label="${1:?Usage: scripts/record-evidence.sh LABEL command [args...]}"
shift
[[ "$label" =~ ^[A-Za-z0-9_-]+$ ]] || { echo 'Use letters, numbers, underscore or hyphen in label' >&2; exit 2; }
[ "$#" -gt 0 ] || exit 2
mkdir -p evidence/verification
file="evidence/verification/${label}-$(date -u '+%Y%m%dT%H%M%SZ').txt"
set +e
(
 printf 'START_UTC=%s\nMACHINE=%s\nCOMMIT=%s\n' "$(date -u '+%Y-%m-%dT%H:%M:%SZ')" "$(hostname)" "$(git rev-parse HEAD)"
 printf 'COMMAND:'; printf ' %q' "$@"; printf '\n'
 "$@"
 rc=$?
 printf '\nEXIT_CODE=%s\nEND_UTC=%s\n' "$rc" "$(date -u '+%Y-%m-%dT%H:%M:%SZ')"
 exit "$rc"
) 2>&1 | tee "$file"
rc=${PIPESTATUS[0]}
set -e
printf '\nSaved actual output: %s\n' "$file"
exit "$rc"
