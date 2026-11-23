# Evidence navigation

- [Current acceptance ledger](../reports/verification-status.json) states exactly
  what still needs real output.
- [Phase 2 historical index](phase2/INDEX.md) explains existing screenshots and their
  actual limits. Historical results do not establish current service availability.
- `verification/` holds new timestamped transcripts and saved captures. Generate
  actual logs with `scripts/record-evidence.sh`; do not write expected output as proof.
- Phase 1 `network/`, `dns/`, `backends/`, `nginx/`, `tls/`, `caching/`, `wireshark/`,
  `failures/` remain preserved. The wrong DNS/record/port, A-down/both-down and
  restored images are historical stage evidence.

Actual 304 in the old caching screenshot is localhost; the updated live check must
show /api/cache-demo through trusted HTTPS by hostname. Phase 1 dig-app/dig-api use
an earlier DNS lease 10.7.21.14; later captures use10.7.17.21. Phase 2 uses the current
10.7.27.145/10.7.27.247 resolver pair.

Evaluator path: README → acceptance ledger → exact artifact paths. Keep actual
capture filenames, packet/frame index, host/time and observed result together so
an exhibit can be found within 30 seconds. Private keys/PF tokens remain outside Git.
