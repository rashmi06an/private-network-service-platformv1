# Phase 2 Evidence — Index (for the evaluator)

Every Phase 2 screenshot, grouped by extension, with what it proves and which machine
it was taken on. Phase 2 addresses: Mac1 `10.7.27.145` (primary DNS) · Mac2 `10.7.25.25`
(edge) · Mac3 `10.7.28.78` (Backend A / standby edge) · Mac4 `10.7.27.247` (Backend B /
backup DNS). See [../../docs/network-inventory.md](../../docs/network-inventory.md) for the
Phase 1 ↔ Phase 2 address mapping.

> **Split-DNS note (applies throughout):** the clients resolve `*.team1.test` via
> `/etc/resolver/team1.test`. A bare `dig app.team1.test` (no `@server`) therefore goes to
> the public resolver (`8.8.8.8` / `1.1.1.1`), which does not know `.test` and returns
> `NXDOMAIN` — this is expected. Private-zone proof uses `dig @10.7.27.145 …` /
> `dig @10.7.27.247 …` or `dscacheutil -q host -a name …`.

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
| `edge-to-backend-http-200.png` *(add)* | Edge → Backend B (`10.7.25.25` → `10.7.27.247:3002`): TCP handshake, `GET /`, `200 OK` JSON — the internal LAN HTTP leg, **unencrypted** (contrast the TLS leg above) |
| `failover-backendA-rst-backendB-200.png` *(add)* | HA failover at packet level: Backend A (`10.7.28.78:3001`) sends `RST`, Backend B serves `200` |

---

See [EVIDENCE-CHECKLIST.md](EVIDENCE-CHECKLIST.md) for the capture status and the two
remaining items (backup-record sync, optional B4 re-shoot). Extension F is live.
