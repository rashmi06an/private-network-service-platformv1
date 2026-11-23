# Phase 2 historical screenshot index

These are historical screenshots, not a complete current acceptance suite. The table
describes actual contents even where an old filename is misleading. New proof goes
in [verification](../verification/) and the [acceptance ledger](../../reports/verification-status.json).

| Screenshot | Actual content / limit |
|---|---|
| [A1-both-resolvers-and-backends-mac3.png](backup-dns/A1-both-resolvers-and-backends-mac3.png) | Mac 3: primary=.25.25, backup=.28.78 (different); backend/HTTPS success. Does not prove synchronized DNS. |
| [A2-backup-dns-listening-mac4.png](backup-dns/A2-backup-dns-listening-mac4.png) | Mac 4 backup UDP/TCP 53 listeners; also shows config-file edits, not proof of final synchronized answers. |
| [A2b-mac4-backend-and-backup-dns.png](backup-dns/A2b-mac4-backend-and-backup-dns.png) | Despite filename, Mac 2 balanced A/B followed by B-only successful requests while A fails. Useful D stage evidence. |
| [A3-note-bare-dig-hits-public-nxdomain.png](backup-dns/A3-note-bare-dig-hits-public-nxdomain.png) | Bare dig uses8.8.8.8 and getsNXDOMAIN; diagnostic split-DNS note, not private-resolver failover. |
| [A3-primary-down-backup-answers-mac2.png](backup-dns/A3-primary-down-backup-answers-mac2.png) | Primary timeout; backup=.28.78 with TTL 0; system=.25.25. Fresh OS backup selection is not established. |
| [primary-dns-listening-mac1.png](backup-dns/primary-dns-listening-mac1.png) | Primary UDP/TCP 53 listener and correct app/api answers; stop/start commands also present. |
| [primary-dns-tcpdump-and-https-mac1.png](backup-dns/primary-dns-tcpdump-and-https-mac1.png) | Team-domain DNS query/answer visible; shown earlier HTTPS block uses an IP host. Do not count it as by-name outage proof. |
| [setup-mac1-dig-tests.png](backup-dns/setup-mac1-dig-tests.png) | Primary stop/timeout/start/answer stages, without a synchronized fresh client/backup trace. |
| [setup-mac1-dns-service-checks.png](backup-dns/setup-mac1-dns-service-checks.png) | Initial timeouts/service and privilege troubleshooting; preserve as diagnostic, not PASS. |
| [setup-mac1-ip-fix-dhcp-rebind.png](backup-dns/setup-mac1-ip-fix-dhcp-rebind.png) | Old lease/config diagnosis and corrections; includes failed lookups during setup. |
| [E2-standby-https-xedge-and-dns-mac2.png](edge-migration/E2-standby-https-xedge-and-dns-mac2.png) | Both DNS servers/system lookup=.28.78; normal by-name HTTPS200, standby header, connected IP=.28.78. Positive cutover exhibit. |
| [E2b-standby-https-both-backends-mac2.png](edge-migration/E2b-standby-https-both-backends-mac2.png) | Standby A/B200 with --resolve. Proves connectivity and trust, bypasses DNS for this test. |
| [E3-cutover-client-connected-ip-mac2.png](edge-migration/E3-cutover-client-connected-ip-mac2.png) | Ends at primary connected IP=.25.25 while primary/backup DNS disagree. Restoration is incomplete; not a clean NEW-standby exhibit. |
| [D1-load-balanced-then-A-down.png](ha-failover/D1-load-balanced-then-A-down.png) | Despite filename, Mac 4 Backend B listener/status and backup DNS=.25.25. Not a load-balancing/A-down trace. |
| [D2-all-B-then-recovered.png](ha-failover/D2-all-B-then-recovered.png) | B-only200 then recovered output includesA/B after 11 seconds; useful D proof. |
| [C1-pf-rules-mac3-backend-a.png](isolation/C1-pf-rules-mac3-backend-a.png) | Mac 3 backup, reachable com.apple/team1_phase2 anchor, allow/block rules, PF token; also both scoped DNS servers. |
| [C2-pf-rules-mac4-backend-b.png](isolation/C2-pf-rules-mac4-backend-b.png) | Mac 4 rules plus actual anchor clear and enable-token release. Existing rollback evidence. |
| [C3-client-blocked-mac1.png](isolation/C3-client-blocked-mac1.png) | Blocked attempts followed later by successful direct backend responses (restored stage). Label the states explicitly. |
| [C3b-client-blocked-timeouts-mac1.png](isolation/C3b-client-blocked-timeouts-mac1.png) | Both backend timeouts and later both direct responses; also app cutover/restoration commands. Rollback outcome is embedded. |
| [C4-edge-reaches-backends-mac2.png](isolation/C4-edge-reaches-backends-mac2.png) | Mac 2 direct HTTP/200 with A/B identity; permitted-source proof. |
| [B1-ttl30-record-countdown-mac1.png](ttl/B1-ttl30-record-countdown-mac1.png) | TTL 30 and record edit commands; not a client TTL countdown. |
| [B2-authoritative-change-new-ip-mac1.png](ttl/B2-authoritative-change-new-ip-mac1.png) | app record cutover/new answer and TTL editing/restart commands; not timed client expiry. |
| [B3-mac1-app-and-ttl-records.png](ttl/B3-mac1-app-and-ttl-records.png) | Two different names: app=.25.25, ttl=.28.78, TTL 30. Not OLD→NEW for one client record. |
| [B3b-dscacheutil-ttl-mac1.png](ttl/B3b-dscacheutil-ttl-mac1.png) | System lookup sees NEW; old cached answer then timed expiry is absent. |
| [B4-attempt1-diagnostic-mac2.png](ttl/B4-attempt1-diagnostic-mac2.png) | Before and after flush remain.25.25. Unsuccessful transition proof. |
| [B4-attempt2-diagnostic-mac2.png](ttl/B4-attempt2-diagnostic-mac2.png) | Before and after flush remain.28.78. Unsuccessful transition proof. |
| [B4-note-backup-missing-ttl-nxdomain-mac4.png](ttl/B4-note-backup-missing-ttl-nxdomain-mac4.png) | Backup TTL record NXDOMAIN at that time; a DNS synchronization defect. |
| [dns-query-response-app-team1.png](wireshark/dns-query-response-app-team1.png) | Project DNS query/response: Mac 2↔Mac 1; ephemeral port61827↔53. |
| [dns-split-behavior-public-nxdomain.png](wireshark/dns-split-behavior-public-nxdomain.png) | Private A answers plus other DNS queries/public forwarding in the historical live config. Not the exact new scoped-only DNS template. |
| [tls-handshake-clienthello-serverhello.png](wireshark/tls-handshake-clienthello-serverhello.png) | TLS 1.3 ClientHello/ServerHello/CCS/encrypted records, ports56853↔8443. Certificate not decoded. |

<<<<<<< HEAD
The two previously requested optional internal-HTTP/RST PNGs are not attached; do
not label them captured. Actual faculty fault evidence is added only when administered.
Use the new verification ledger rather than the historical filename checklist.
=======
---

## Extension A — Backup DNS resolver  → `backup-dns/`

| File | Machine | Proves |
|------|---------|--------|
| `A1-both-resolvers-and-backends-mac3.png` | Mac 3 | Primary (`@10.7.27.145`) and backup (`@10.7.27.247`) both resolve; both backends answer; HTTPS `X-Backend` works |
| `A2-backup-dns-listening-mac4.png` | Mac 4 | Backup dnsmasq **listening** on `10.7.27.247:53` (UDP+TCP) — `lsof` |
| `A2b-mac4-backend-and-backup-dns.png` | Mac 4 | Backend B + backup DNS both up on Mac 4; port check |
| `A3-primary-down-backup-answers-mac2.png` | Mac 2 | **Failover:** primary (`@10.7.27.145`) times out, backup (`@10.7.27.247`) answers, `dscacheutil` still resolves |
| `A3-note-bare-dig-hits-public-nxdomain.png` | Mac 4 | Teaching note: a bare `dig` goes to `8.8.8.8` → `NXDOMAIN` (why we name the server) |
| `primary-dns-listening-mac1.png` | Mac 1 | Primary dnsmasq listening on `10.7.27.145:53` |
| `primary-dns-tcpdump-and-https-mac1.png` | Mac 1 | `tcpdump port 53` DNS query/response + a working HTTPS `200` |
| `setup-mac1-*.png` | Mac 1 | Primary DNS service checks, the DHCP IP re-fix, and dig tests |

## Extension B — DNS TTL & controlled record change  → `ttl/`

| File | Machine | Proves |
|------|---------|--------|
| `B1-ttl30-record-countdown-mac1.png` | Mac 1 | `ttl.team1.test` served with **TTL = 30** |
| `B2-authoritative-change-new-ip-mac1.png` | Mac 1 | After the record change, the authoritative `dig` shows the **new IP (`10.7.28.78`) immediately** |
| `B3-mac1-app-and-ttl-records.png` | Mac 1 | `app` = `10.7.25.25`, `ttl` = `10.7.28.78` side by side |
| `B3b-dscacheutil-ttl-mac1.png` | Mac 1 | System-cache view of the record |
| `B4-attempt1/2-diagnostic-mac2.png` | Mac 2 | Working through the manual-flush demo (dual-resolver + ordering) |
| `B4-note-backup-missing-ttl-nxdomain-mac4.png` | Mac 4 | Diagnosis: the backup lacked the `ttl` record (NXDOMAIN) — fixed by syncing records |

> **Manual cache-flush → immediate change** is also shown directly under Extension E
> (`edge-migration/`), where a flush switches the client from the primary to the standby edge.

## Extension C — Backend service isolation (pf)  → `isolation/`

| File | Machine | Proves |
|------|---------|--------|
| `C1-pf-rules-mac3-backend-a.png` | Mac 3 | pf anchor loaded: allow `10.7.25.25` → `:3001`, block all else; `pf enabled` |
| `C2-pf-rules-mac4-backend-b.png` | Mac 4 | Same for `:3002` |
| `C3-client-blocked-mac1.png` | Mac 1 | Client direct `curl` to `:3001`/`:3002` → **`curl (28) … Timeout`** (blocked) |
| `C3b-client-blocked-timeouts-mac1.png` | Mac 1 | More blocked-connection timeouts |
| `C4-edge-reaches-backends-mac2.png` | Mac 2 | The **edge** reaches both backends directly → `200` + `X-Backend` A/B |

## Extension D — HA failover  → `ha-failover/`

| File | Machine | Proves |
|------|---------|--------|
| `D1-load-balanced-then-A-down.png` | client | Both up: `X-Backend` alternates A/B |
| `D2-all-B-then-recovered.png` | client | Backend A down → all `HTTP 200` + `X-Backend: B`; A restarted → A/B alternate again |

## Extension E — Controlled edge migration (DNS cutover)  → `edge-migration/`

| File | Machine | Proves |
|------|---------|--------|
| `E2-standby-https-xedge-and-dns-mac2.png` | Mac 2 | HTTPS to standby → `200`, header **`X-Edge: standby-mac3`** |
| `E2b-standby-https-both-backends-mac2.png` | Mac 2 | Standby edge still load-balances A/B (`X-Edge: standby-mac3`) |
| `E3-cutover-client-connected-ip-mac2.png` | Mac 2 | After the DNS cutover + flush, the client connects to the new edge (`CONNECTED_IP`) |

## Extension F — Faculty-injected troubleshooting  → `troubleshooting/`

Performed live during Review 2. Diagnosis order: DNS → TCP → TLS → application.
(Place the demo-day screenshots + a one-line note of the fault here.)

## Bonus — Wireshark protocol-flow captures  → `wireshark/`

| File | Proves |
|------|--------|
| `dns-query-response-app-team1.png` | DNS query + response for `app.team1.test` (UDP/53) |
| `tls-handshake-clienthello-serverhello.png` | TLS handshake: Client Hello → Server Hello, Change Cipher Spec, Application Data (client ↔ edge, encrypted) |
| `dns-split-behavior-public-nxdomain.png` | Split-DNS in action: `A team1.test` → team DNS; `AAAA/SVCB` → `8.8.8.8`/`1.1.1.1` → "No such name" |

---

See [EVIDENCE-CHECKLIST.md](EVIDENCE-CHECKLIST.md) for the full capture manifest. Extension F
(faculty-injected fault) is diagnosed live during Review 2.
>>>>>>> ac742fe (Fixed report duality)
