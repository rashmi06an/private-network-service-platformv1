# CN Team 1 — Phase 2 configuration and evidence bundle

Faculty scope: **Harden, Recover and Troubleshoot**, mandatory Extensions A–F.

Updated LAN observations (20 Nov 2026; DHCP addresses may change):

| Machine | Operator | IP | Services |
|---|---|---|---|
| Mac 1 | Rashmi Anand | 10.7.27.145 | Primary DNS (dnsmasq, UDP/TCP 53) |
| Mac 2 | Samiksha Jangid | 10.7.25.25 | Primary nginx TLS edge (8443) |
| Mac 3 | Shubhaang Kataruka | 10.7.28.78 | Flask A (3001), standby nginx (8443 during cutover) |
| Mac 4 | Ankit Raj Singh | 10.7.27.247 | Flask B (3002), backup DNS (53) |

**Main hostname:** app.team1.test (api.team1.test also points at active edge). The primary-edge address is 10.7.25.25; the standby-edge address during the migration demonstration is 10.7.28.78.

## Included files

- `config/mac1-primary-dns.conf.example` — project-specific dnsmasq settings, synthesized from confirmed Mac 1 output; it is not the entire active `/opt/homebrew/etc/dnsmasq.conf`.
- `config/mac2-nginx.conf.example` — documented reconstructed nginx example; verify against actual live Mac 2 configuration before using. The Phase 1 source already tracks an edge config.
- `config/mac3-firewall.pf` and `config/mac4-firewall.pf` — macOS PF allowlist demonstration for backend ports.
- `config/mac3-standby-nginx.conf.example` — reconstructed, sanitized standby nginx config; certificate/key **paths only**, no keys.
- `config/mac4-backup-dns.conf.example` — project-specific backup dnsmasq file based on Mac 4's terminal output.
- `scripts/final-check.sh` — non-destructive client check, prints PASS/FAIL and timestamped evidence, but does not prove an outage or cache behavior by itself.
- `evidence/phase2/observed-terminal-results.md` — compact observations copied from the actual user-shared terminal logs, with gaps clearly stated.
- `evidence/phase2/README.md` — screenshots/index and remaining acceptance checks.

These are **submission examples + observed output**, not a replacement for full live machine configs or screenshots. Never copy example files over active configs without syntax testing and a backup. Do not commit TLS private keys, CA signing keys, passwords, or `.venv`.

## Faculty extensions

| Extension | Evidence/status from supplied logs |
|---|---|
| A — Backup DNS | Both servers answer and log queries; clients successfully resolve during DNS failover tests, but simultaneous primary-off verification should be timestamped |
| B — DNS TTL | TTL 30, old cached answer, updated answer after 35 s verified; manual flush before/after changed **not yet proven** |
| C — Backend isolation | Mac 2 allowed; Mac 1 blocked to both ports; rollback restored; PASS based on logs |
| D — Backend failover | A down: 10/10 `HTTP 200 / X-Backend B`; after A restart, both A/B appear; PASS based on logs |
| E — DNS edge migration | Standby nginx listening, valid certificate and config; cutover successful per operator, but provided logs show DNS servers disagreed *after* alleged restore; recheck both |
| F — Faculty-injected fault | Cannot be pre-certified; review layered troubleshooting evidence and rehearse |

## Final live-state sanity checks

```bash
# From a client Mac; run while connected to the project LAN
bash phase2/scripts/final-check.sh
```

In particular, **both primary and backup DNS** must resolve app.team1.test to **10.7.25.25** after the migration rollback. The user-supplied Nov 20 Mac 3 log at 20:25 IST showed Mac 1 returning 10.7.25.25 but Mac 4 returning **10.7.28.78**. Correct this mismatch on Mac 4 if it still exists; never assume it was restored.

Report is intentionally **excluded** from this bundle as requested.
