<<<<<<< HEAD
# Acceptance checklist

The single current checklist is [reports/verification-status.json](../../reports/verification-status.json).
Each item lists mandatory proof, reviewed status and exact artifact paths.
Do not count an old filename or an expected-result paragraph as a pass.

Required new evidence: all-pairs inventory; matched DNS/settings/failover; timed
natural TTL and successful manual flush; isolation allow/deny/HTTPS/rollback; HA
balanced/A-down/recovered; valid standby and old/fresh/new cutover with both-server
restore; saved packet capture with frame index; end-to-end caching304; HTTP/2 where
supported; rehearsal findings. Actual faculty challenge/personal viva remain live.

See [actual historical contents](INDEX.md), [member commands](../../docs/team-commands.md)
and [capture guide](../../docs/packet-evidence.md). No B4 requirement is optional.
=======
# Phase 2 Evidence — Capture Manifest

All Phase 2 evidence is captured and filed. Every screenshot listed below exists in the
folder shown. For the full labeled map (what each shot proves, and which machine it was
taken on) see [INDEX.md](INDEX.md).

Phase 2 addresses: Mac1 `10.7.27.145` (DNS) · Mac2 `10.7.25.25` (edge) · Mac3 `10.7.28.78`
(Backend A / standby) · Mac4 `10.7.27.247` (Backend B / backup DNS).

---

## A — Backup DNS → `backup-dns/`

- `A1-both-resolvers-and-backends-mac3.png` — primary (`@10.7.27.145`) and backup (`@10.7.27.247`) both resolve `app.team1.test` → `10.7.25.25`; both backends answer; HTTPS `X-Backend` works
- `A2-backup-dns-listening-mac4.png` — backup dnsmasq listening on `10.7.27.247:53` (UDP+TCP)
- `A2b-mac4-backend-and-backup-dns.png` — Backend B + backup DNS both up on Mac 4
- `A3-primary-down-backup-answers-mac2.png` — primary stopped → `@10.7.27.145` times out, `@10.7.27.247` answers, `dscacheutil` resolves
- `A3-note-bare-dig-hits-public-nxdomain.png` — teaching note: a bare `dig` goes to `8.8.8.8` → NXDOMAIN
- `primary-dns-listening-mac1.png` · `primary-dns-tcpdump-and-https-mac1.png` · `setup-mac1-*.png` — primary DNS service checks, `tcpdump port 53`, the DHCP IP re-fix, and a working HTTPS `200`

## B — TTL & record change → `ttl/`

- `B1-ttl30-record-countdown-mac1.png` — `ttl.team1.test` served with TTL = 30
- `B2-authoritative-change-new-ip-mac1.png` — after the record change + restart, authoritative `dig` shows the new IP (`10.7.28.78`) immediately
- `B3-mac1-app-and-ttl-records.png` · `B3b-dscacheutil-ttl-mac1.png` — `app` vs `ttl` records side by side + system-cache view
- `B4-attempt1-diagnostic-mac2.png` · `B4-attempt2-diagnostic-mac2.png` · `B4-note-backup-missing-ttl-nxdomain-mac4.png` — manual-flush demo (dual-resolver + ordering) and the record-sync diagnosis

> Manual cache-flush → immediate change is also shown directly under Extension E, where a
> flush switches the client from the primary to the standby edge.

## C — Service isolation → `isolation/`

- `C1-pf-rules-mac3-backend-a.png` — Mac 3 pf anchor: allow `10.7.25.25` → `:3001`, block all else; `pf enabled`
- `C2-pf-rules-mac4-backend-b.png` — same for `:3002`
- `C3-client-blocked-mac1.png` · `C3b-client-blocked-timeouts-mac1.png` — client direct `curl` to `:3001`/`:3002` → `curl (28) … Timeout` (blocked)
- `C4-edge-reaches-backends-mac2.png` — the edge reaches both backends → `200` + `X-Backend` A/B

## D — Backend failover → `ha-failover/`

- `D1-load-balanced-then-A-down.png` — both up: `X-Backend` alternates A/B
- `D2-all-B-then-recovered.png` — Backend A stopped → requests all `HTTP 200` + `X-Backend: B`; A restarted → A/B alternate again

## E — Standby edge migration → `edge-migration/`

- `E2-standby-https-xedge-and-dns-mac2.png` — HTTPS to standby → `200`, header `X-Edge: standby-mac3`
- `E2b-standby-https-both-backends-mac2.png` — standby edge still load-balances A/B
- `E3-cutover-client-connected-ip-mac2.png` — after the DNS cutover + flush, the client connects to the new edge

## F — Faculty-injected fault → `troubleshooting/`

Diagnosed live during Review 2, in the order DNS → TCP → TLS → application. The demo-day
screenshots and a one-line note of the fault, the affected layer, and the fix/isolation are
placed in this folder at that time.

## Bonus — Wireshark protocol-flow captures → `wireshark/`

- `dns-query-response-app-team1.png` — DNS query + response for `app.team1.test` (UDP/53)
- `tls-handshake-clienthello-serverhello.png` — TLS handshake (Client Hello → Server Hello), encrypted Application Data
- `dns-split-behavior-public-nxdomain.png` — split-DNS behaviour (private zone → team DNS; public types → NXDOMAIN)

---

### Split-DNS note (important for A3 and the cutover demos)

These Macs resolve the private zone via `/etc/resolver/team1.test` (which lists the team DNS
servers). Consequences:

- `dig app.team1.test` **without `@server`** → uses the global resolver (8.8.8.8) → NXDOMAIN.
  This is expected, not a failure — just don't use it as proof.
- To query the team DNS, use `dig @10.7.27.145 …` / `dig @10.7.27.247 …` (explicit), or
  `dscacheutil -q host -a name …` / a browser (system resolver, honours `/etc/resolver`).
- During a cutover, change the record on **every** DNS server (primary *and* backup), because
  a client may be answered by either one.
>>>>>>> ac742fe (Fixed report duality)
