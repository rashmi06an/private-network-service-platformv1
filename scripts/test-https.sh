#!/usr/bin/env bash
# Task E + F — verify HTTPS through the edge and show caching headers.
# Run from a client Mac that trusts the local CA (no -k flag by design).
set -euo pipefail

URL="https://app.team1.test/api/status"

echo "== HTTPS request (full headers) =="
curl -v "$URL" 2>&1 | sed -n '1,40p'
echo

echo "== Response headers only (look for Cache-Control / ETag) =="
curl -I "$URL"
echo

echo "== Conditional request (expect 304 Not Modified) =="
ETAG=$(curl -sI "$URL" | awk -F': ' 'tolower($1)=="etag"{print $2}' | tr -d '\r')
if [ -n "${ETAG:-}" ]; then
    curl -s -o /dev/null -w "HTTP %{http_code}\n" -H "If-None-Match: ${ETAG}" "$URL"
else
    echo "No ETag returned; enable 'etag on;' in nginx to test conditional requests."
fi
