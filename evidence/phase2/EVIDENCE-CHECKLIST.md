# Phase 2 Evidence Checklist

Save each screenshot with the exact filename below, in the folder shown. Status:
- ✅ **have** — already captured in the screenshots shared on 20 Nov (just rename/drop in)
- ⚠️ **redo** — captured but needs a cleaner/overlapping shot to fully count
- ⬜ **todo** — not yet captured

Phase 2 addresses: Mac1 `10.7.27.145` (DNS) · Mac2 `10.7.25.25` (edge) · Mac3 `10.7.28.78` (Backend A / standby) · Mac4 `10.7.27.247` (Backend B / backup DNS).

---

## A — Backup DNS → `backup-dns/`

| File | Status | What it must show |
|------|--------|-------------------|
| `A1-both-resolvers.png` | ✅ have | `dig @10.7.27.145` and `dig @10.7.27.247 app.team1.test` both → `10.7.25.25` |
| `A2-mac4-query-log.png` | ✅ have | Mac 4 `lsof` shows backup dnsmasq listening on `10.7.27.247:53` (UDP+TCP) |
| `A3-primary-stopped-backup-answers.png` | ✅ have | Primary (Mac 1) stopped → `dig @10.7.27.145` times out, `dig @10.7.27.247` answers, `dscacheutil` resolves. **Cleanup:** backup was returning `10.7.28.78` (stale cutover value) while the cache showed `10.7.25.25` — re-sync the backup record to `10.7.25.25` (see outstanding #2) and ideally re-shoot so all three agree. |
| `A4-client-https-after-flush.png` | ✅ have | client `curl https://app.team1.test:8443/api/status` → `200` while primary is down |

## B — TTL & record change → `ttl/`

| File | Status | What it must show |
|------|--------|-------------------|
| `B1-ttl30-countdown.png` | ✅ have | `dig @10.7.27.145 ttl.team1.test +noall +answer` → `ttl.team1.test. 30 IN A 10.7.25.25` (TTL = 30) |
| `B2-authoritative-new-ip.png` | ✅ have | after changing the record + restart, `dig` shows the NEW ip (`10.7.28.78`) immediately |
| `B3-client-cached-then-expiry.png` | ✅ have | client cache keeps OLD ip, then shows NEW after ~35s expiry |
| `B4-manual-flush-before-after.png` | ⚠️ redo | **Change `ttl.team1.test` → `10.7.28.78` on BOTH DNS servers (Mac 1 primary AND Mac 4 backup), not just Mac 1** — otherwise the backup keeps answering the old IP and after-flush stays `10.7.25.25` (that was the bug). Then on a client: `dscacheutil -q host` = OLD `10.7.25.25` (before), `flushcache; killall -HUP mDNSResponder`, `dscacheutil -q host` = NEW `10.7.28.78` (after). Restore both servers afterwards. |

## C — Service isolation → `isolation/`

| File | Status | What it must show |
|------|--------|-------------------|
| `C1-pf-rules-mac3.png` | ✅ have | Mac 3: pf anchor loaded (`pass … from 10.7.25.25 … port 3001`, `block … port 3001`), `pf enabled` |
| `C2-pf-rules-mac4.png` | ✅ have | Mac 4: same for port 3002 |
| `C3-mac1-blocked.png` | ✅ have | Mac 1 direct `curl http://10.7.28.78:3001` and `…:27.247:3002` → `curl (28) … Timeout` |
| `C4-edge-200.png` | ✅ have | Mac 2 direct `curl` to `:3001` and `:3002` → `200` + `X-Backend` A/B |
| `C5-rollback-restored.png` | ✅ have | after `pfctl -F rules`, Mac 1 can reach the backends again (`{"backend":...}`) |

## D — Backend failover → `ha-failover/`

| File | Status | What it must show |
|------|--------|-------------------|
| `D1-balanced.png` | ✅ have | both up: `X-Backend` alternates A/B |
| `D2-A-down-all-B-200.png` | ✅ have | Backend A stopped: ~10 requests all `HTTP 200` + `X-Backend: B` |
| `D3-rebalanced.png` | ✅ have | Backend A restarted: A/B alternate again |

## E — Standby edge migration → `edge-migration/`

| File | Status | What it must show |
|------|--------|-------------------|
| `E1-standby-config-start.png` | ✅ have | Mac 3 standby nginx: `nginx -t` OK + start without fatal error |
| `E2-standby-https-xedge.png` | ✅ have | HTTPS to standby → `200`, header `X-Edge: standby-mac3`, `X-Backend` A/B |
| `E3-dns-cutover.png` | ✅ have | Mac 1 repoints record; `dig app.team1.test` → `10.7.28.78` (standby) |
| `E4-restored.png` | ✅ have | record restored to `10.7.25.25`; standby stopped |

## F — Faculty-injected fault → `troubleshooting/`

| File | Status | What it must show |
|------|--------|-------------------|
| `F1-diagnosis.png` + note | ⬜ live | On demo day: `dig → nc → curl -vI → backend curl` sequence, plus a note of the fault, the layer, and the fix/isolation |

---

## Summary of what is still outstanding

1. ~~Sync the backup DNS~~ — **DONE.** Mac 4 now serves `app/api/ttl.team1.test → 10.7.25.25`
   (verified `dig @10.7.27.247 app.team1.test +short → 10.7.25.25`), matching the primary.
2. **B4** — *optional/redundant.* The manual-flush → immediate-change behaviour is already
   shown under Extension E (flush switches the client from primary to standby edge). Re-shoot
   only if you want the literal `ttl.team1.test` before/after; otherwise cite E and explain in viva.
3. **F1** (live) — happens during Review 2; nothing to pre-capture.

Bonus Wireshark captures already in `evidence/phase2/wireshark/`: DNS query/response,
TLS handshake, and split-DNS behaviour. **Add these two newer ones** (save into the same folder):
- `edge-to-backend-http-200.png` — edge `10.7.25.25` → Backend B `10.7.27.247:3002`: TCP handshake,
  `GET / HTTP/1.1`, `200 OK` JSON (internal LAN HTTP, unencrypted — contrast with the TLS leg).
- `failover-backendA-rst-backendB-200.png` — Backend A `10.7.28.78:3001` sends `RST`, Backend B
  serves `200` — HA failover visible at the packet level.

Everything else (A1, **A2**, A4, all of B1–B3, C1–C5, D1–D3, E1–E4) is already captured in the
screenshots — just rename to the filenames above and drop into the folders.

### Split-DNS gotcha (important for A3/B4)

These Macs resolve the private zone via `/etc/resolver/team1.test` (which lists the
team DNS servers). Consequences:
- `dig app.team1.test` **without `@server`** → uses the global resolver (8.8.8.8) →
  `NXDOMAIN`. This is expected, not a failure — just don't use it as proof.
- To query the team DNS, use `dig @10.7.27.145 …` / `dig @10.7.27.247 …` (explicit), or
  `dscacheutil -q host -a name …` / a browser (system resolver, honours `/etc/resolver`).
- During a cutover, change the record on **every** DNS server (primary *and* backup),
  because a client may be answered by either one.
