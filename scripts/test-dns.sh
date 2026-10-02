#!/usr/bin/env bash
# Task B — verify the private DNS server resolves the project domains.
# Run from any client Mac configured to use Mac 1 as its DNS resolver.
set -euo pipefail

DOMAINS=("app.team1.test" "api.team1.test")

echo "== DNS resolution test =="
for d in "${DOMAINS[@]}"; do
    echo "--- dig $d ---"
    dig +noall +answer "$d"
    echo
done

echo "Expected: both names resolve to the private IP of Mac 2 (the nginx edge)."
