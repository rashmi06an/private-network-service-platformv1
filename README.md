# Private Network Service Platform

> **Computer Networks — Course Project · Team Scout Regiment**
> **Phase 1 (Build & Observe) — complete** · **Phase 2 (Harden, Recover & Troubleshoot) — complete**

A fully **local** private network service on four macOS laptops — no cloud, no
pre-configured servers. A client types a private domain (`https://app.team1.test:8443`);
the name resolves through our own DNS server, connects over HTTPS to an nginx reverse
proxy, and is load-balanced to one of two backend services. Every protocol layer
(DNS → TCP → TLS → HTTP) is captured in Wireshark. Phase 2 then adds a backup DNS,
TTL-based cutover, backend firewall isolation, HA failover, and a standby edge.

```
Client -> Private DNS (Mac 1) -> nginx edge, TLS, load balancer (Mac 2) -> Backend A (Mac 3) / Backend B (Mac 4)
```

---

## Team

| Name | Enrollment No. | Machine | Phase 1 role | Phase 2 additions |
|------|----------------|---------|--------------|-------------------|
| Rashmi Anand | 2401010374 | Mac 1 | Private DNS (dnsmasq) + Test Client | TTL / record-change cutover (Ext B) |
| Samiksha Jangid | 2401010410 | Mac 2 | nginx Edge — HTTPS/TLS + Load Balancer | HA failover config (Ext D) |
| Shubhaang Kataruka | 2401010450 | Mac 3 | Backend A (Flask REST) | Standby edge (Ext E) + firewall A (Ext C) |
| Ankit Raj Singh | 2401010075 | Mac 4 | Backend B (Flask REST) + Test Client | Backup DNS (Ext A) + firewall B (Ext C) |

---

## Topology & addressing

![Network topology diagram](evidence/network/topology-diagram.png)

All four Macs share one private Wi-Fi/LAN (`10.7.0.0/19`, gateway `10.7.0.1`, `en0`).

> **Two IP columns:** the LAN IPs changed between Phase 1 and Phase 2 because DHCP
> issued new leases in each session. The **domain names and MAC addresses stayed the
> same** — which is exactly the point of running DNS. Full table with MACs:
> **[docs/network-inventory.md](docs/network-inventory.md)**.

| Machine | Role | Phase 1 address | Phase 2 address | Cloud equivalent |
|---------|------|-----------------|-----------------|------------------|
| Mac 1 | Private DNS (dnsmasq) + client | `10.7.17.21:53` | `10.7.27.145:53` | Managed DNS (Route 53) |
| Mac 2 | nginx edge: TLS + load balancer | `10.7.7.9:8443` | `10.7.25.25:8443` | Cloud load balancer / CDN |
| Mac 3 | Backend A (REST) + standby edge (P2) | `10.7.21.15:3001` | `10.7.28.78:3001` | App server instance A |
| Mac 4 | Backend B (REST) + backup DNS (P2) | `10.7.23.47:3002` | `10.7.27.247:3002` | App server instance B |

**Domain:** `app.team1.test` / `api.team1.test` resolve to Mac 2 (`10.7.7.9` in Phase 1,
`10.7.25.25` in Phase 2). Phase 2 adds `ttl.team1.test` (30 s TTL) for the cutover demo.

---

## Architecture — one request, layer by layer

```
Client (Mac 1 / Mac 4)
  | 1. DNS QUERY     -- UDP 53   -->  Mac 1 (dnsmasq)   "app.team1.test = ?"  -> edge IP
  | 2. TCP HANDSHAKE -- TCP 8443 -->  Mac 2   SYN -> SYN-ACK -> ACK
  | 3. TLS HANDSHAKE -->              Mac 2   ClientHello -> ServerHello -> Certificate -> Finished
  | 4. HTTPS REQUEST -->              Mac 2   GET /api/status   (payload now encrypted)
  v
Mac 2  nginx reverse proxy + round-robin load balancer
  |--> Mac 3  Backend A :3001   (X-Backend: A)
  |--> Mac 4  Backend B :3002   (X-Backend: B)
```

| Layer | Protocol | Addressing |
|-------|----------|------------|
| Application | DNS / HTTP(S) | ports 53/UDP, 8443/TCP |
| Session/Transport | TLS | port 8443/TCP |
| Transport | TCP | ports 8443/TCP, 3001/3002 |
| Network | IP | IP addresses (10.7.x.x) — no ports at this layer |
| Link | Ethernet | MAC addresses — no ports at this layer |

Full diagram, OSI/TCP-IP mapping, and explanation: **[docs/architecture.md](docs/architecture.md)**.

---

## Repository structure

```
backend-a/     Flask backend A — /, /api/status, /api/cache-demo   (:3001, X-Backend: A)
backend-b/     Flask backend B — same endpoints                    (:3002, X-Backend: B)
dns/           dnsmasq configs: Phase 1, Phase 2 primary (+TTL), backup; client resolver setup
edge/          nginx reverse proxy / LB + TLS; Phase 2 HA + standby-edge configs
firewall/      Phase 2 pf rules — backend service isolation (Ext C) + apply/rollback README
scripts/       test scripts — Phase 1 (DNS/backends/HTTPS/LB) + Phase 2 (backup-DNS/TTL/HA/isolation)
docs/          architecture, network inventory (P1+P2), demo runbooks (P1 + P2), screenshot guide
reports/       phase1-report.md + phase2-report.md
evidence/      screenshots & captures, one folder per layer:
               network/ dns/ backends/ nginx/ tls/ caching/ wireshark/ failures/   (Phase 1)
               phase2/{backup-dns, ttl, isolation, ha-failover, edge-migration,
                       troubleshooting, wireshark}/ + INDEX.md + EVIDENCE-CHECKLIST.md
```

---

## Run

**Backends (Mac 3 / Mac 4):**
```bash
cd backend-a            # or backend-b on Mac 4
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
python3 app.py          # A -> 0.0.0.0:3001 ,  B -> 0.0.0.0:3002
```
**Primary DNS (Mac 1):** `sudo brew services start dnsmasq`
— Phase 1 config [dns/dnsmasq.conf.example](dns/dnsmasq.conf.example) ·
Phase 2 config [dns/dnsmasq-phase2.conf.example](dns/dnsmasq-phase2.conf.example)
**Edge (Mac 2):** `sudo nginx -t && sudo nginx`
— [edge/nginx-phase2.conf.example](edge/nginx-phase2.conf.example) + [edge/tls.conf.example](edge/tls.conf.example)
**Backup DNS (Mac 4):** `sudo brew services start dnsmasq` — [dns/backup-dnsmasq.conf.example](dns/backup-dnsmasq.conf.example)
**Standby edge (Mac 3, for Ext E):** [edge/standby-nginx.conf.example](edge/standby-nginx.conf.example)

---

## Verify (from a client)

```bash
# Phase 1
scripts/test-dns.sh               # resolves app/api.team1.test via Mac 1
scripts/test-backends.sh          # both backends answer
scripts/test-https.sh             # HTTPS + Cache-Control headers
scripts/test-load-balancing.sh    # X-Backend alternates A / B
# Phase 2
scripts/test-backup-dns.sh        # primary + backup both resolve
scripts/test-dns-ttl.sh           # 30 s TTL countdown on ttl.team1.test
scripts/test-backend-isolation.sh # direct :3001/:3002 blocked; by-name via edge works
scripts/test-ha-failover.sh       # service survives a backend going down
```

> **Split-DNS note:** clients resolve `*.team1.test` via `/etc/resolver/team1.test`, so a
> bare `dig app.team1.test` goes to the public resolver (`8.8.8.8`) and returns NXDOMAIN.
> Use `dig @10.7.27.145 …` / `dig @10.7.27.247 …` or `dscacheutil -q host -a name …`.

---

## Phase 1 — Build & Observe (all tasks complete)

| Task | What it proves | Evidence |
|------|----------------|----------|
| A | Private LAN + topology + ping | [evidence/network/](evidence/network/) |
| B | Private DNS + two client resolvers | [evidence/dns/](evidence/dns/) |
| C | Two REST backends, `X-Backend` header | [evidence/backends/](evidence/backends/) |
| D | nginx round-robin load balancing | [evidence/nginx/](evidence/nginx/) |
| E | HTTPS / TLS termination (trusted cert) | [evidence/tls/](evidence/tls/) |
| F | HTTP caching (Cache-Control + 304) | [evidence/caching/](evidence/caching/) |
| G | Wireshark: DNS, TCP, TLS, encrypted data | [evidence/wireshark/](evidence/wireshark/) |

### Phase 1 failure demonstrations (Section 6.3)

| Scenario | Observation | Evidence |
|----------|-------------|----------|
| Wrong DNS server on a client | Lookup fails though the IP is reachable — DNS and IP are independent | `evidence/failures/wrong-dns-server.png` |
| DNS record → wrong IP | Resolves but reaches the wrong host — DNS is a directory, not a connection | `evidence/failures/wrong-dns-record.png` |
| One backend stopped | Edge keeps serving via the other backend | `evidence/failures/backend-a-down.png` |
| Both backends stopped | DNS/TLS fine, nginx returns `502` — where the edge ends and the backend begins | `evidence/failures/both-down-502.png` |
| Wrong destination port | Host reachable, port connection fails — ports and IPs are separate | `evidence/failures/wrong-port.png` |

Full write-up: **[reports/phase1-report.md](reports/phase1-report.md)** ·
demo commands: **[docs/demo-runbook.md](docs/demo-runbook.md)**.

---

## Phase 2 — Harden, Recover & Troubleshoot (all extensions complete)

Phase 2 extends the same network (it is not rebuilt). Addresses below are **Phase 2** IPs.

![Phase 2 hardened topology](evidence/network/topology-phase2.png)

*Hardened topology (Phase 2 addresses): backup DNS (Mac 4), standby edge (Mac 3), backend
firewall (Ext C), HA failover (Ext D), dashed line = Ext E DNS cutover.*

| Ext | What it adds | Where it runs | Config / script | Evidence |
|-----|--------------|---------------|-----------------|----------|
| A | Backup DNS resolver + client failover | Mac 4 (`10.7.27.247`) | [dns/backup-dnsmasq.conf.example](dns/backup-dnsmasq.conf.example) · [scripts/test-backup-dns.sh](scripts/test-backup-dns.sh) | [evidence/phase2/backup-dns/](evidence/phase2/backup-dns/) |
| B | 30 s TTL + controlled record change | Mac 1 (`10.7.27.145`) | [dns/dnsmasq-phase2.conf.example](dns/dnsmasq-phase2.conf.example) · [scripts/test-dns-ttl.sh](scripts/test-dns-ttl.sh) | [evidence/phase2/ttl/](evidence/phase2/ttl/) |
| C | Backend firewall isolation (edge-only) | Mac 3 & Mac 4 | [firewall/](firewall/) · [scripts/test-backend-isolation.sh](scripts/test-backend-isolation.sh) | [evidence/phase2/isolation/](evidence/phase2/isolation/) |
| D | HA failover (passive health checks) | Mac 2 (`10.7.25.25`) | [edge/nginx-phase2.conf.example](edge/nginx-phase2.conf.example) · [scripts/test-ha-failover.sh](scripts/test-ha-failover.sh) | [evidence/phase2/ha-failover/](evidence/phase2/ha-failover/) |
| E | Controlled edge migration (DNS cutover) | standby on Mac 3 (`10.7.28.78`) | [edge/standby-nginx.conf.example](edge/standby-nginx.conf.example) | [evidence/phase2/edge-migration/](evidence/phase2/edge-migration/) |
| F | Faculty-injected troubleshooting | live, all machines | layer-by-layer method in the runbook | [evidence/phase2/troubleshooting/](evidence/phase2/troubleshooting/) |

**📂 Evidence map for the evaluator:** every screenshot is listed, labeled, and explained in
**[evidence/phase2/INDEX.md](evidence/phase2/INDEX.md)**. Capture status and remaining items:
**[evidence/phase2/EVIDENCE-CHECKLIST.md](evidence/phase2/EVIDENCE-CHECKLIST.md)**.

Full write-up: **[reports/phase2-report.md](reports/phase2-report.md)** ·
demo commands: **[docs/phase2-demo-runbook.md](docs/phase2-demo-runbook.md)** ·
per-Mac capture guide: **[docs/phase2-screenshot-commands.md](docs/phase2-screenshot-commands.md)** ·
client both-resolvers setup: **[dns/client-dns-setup.md](dns/client-dns-setup.md)**.

---

## Course-topic mapping (OSI vs TCP/IP)

| Course topic | Where it appears in this project |
|--------------|----------------------------------|
| Moving data through the core | Client request crosses the LAN to the edge and back — captured in Wireshark |
| OSI vs TCP/IP model | DNS/HTTP = Application · TLS = Session/Transport · TCP/UDP = Transport · IP = Network · Ethernet = Link |
| Devices, topologies, cloud concepts | Local topology (Mac 1–4) mapped to cloud roles (Route 53, cloud LB, app instances) |
| HTTP/1.1, HTTP/2, REST | REST API on both backends; HTTP/1.1 shown (HTTP/2 enabled on the edge) |
| HTTPS and TLS | TLS terminated at nginx; handshake + certificate validation captured |
| Transport layer, ports, TCP/UDP | Service ports and the TCP three-way handshake identified in the capture |
| Reliable data transfer, TCP flow control | Sequence/acknowledgement numbers shown in the handshake |
| Caching | `Cache-Control` + `ETag` with a `304 Not Modified` conditional request |
| Cloud load balancing | nginx round-robin + passive HA failover across two backends |
| DNS and Route 53 concepts | Private zone, backup resolver, TTL-based cutover, DNS-driven edge migration |

---

## Key documents

- **[reports/phase1-report.md](reports/phase1-report.md)** — Phase 1 report + results
- **[reports/phase2-report.md](reports/phase2-report.md)** — Phase 2 report (verified / pending outcomes)
- **[docs/architecture-document.pdf](docs/architecture-document.pdf)** — Architecture Document, **PDF** (Phase 1 + Phase 2 divisions; topology, roles/IP table, request-flow per layer)
- **[docs/architecture-document.html](docs/architecture-document.html)** — same document as HTML (re-print to PDF after editing)
- **[docs/architecture.md](docs/architecture.md)** — same two-division content in Markdown (topology, roles/IP table, request-flow, P1 + P2)
- **[edge/tls-setup-notes.md](edge/tls-setup-notes.md)** — TLS certificate generation + client-trust steps
- **[docs/network-inventory.md](docs/network-inventory.md)** — IP / MAC / service tables (Phase 1 + Phase 2)
- **[docs/demo-runbook.md](docs/demo-runbook.md)** · **[docs/phase2-demo-runbook.md](docs/phase2-demo-runbook.md)** — live demo commands
- **[evidence/phase2/INDEX.md](evidence/phase2/INDEX.md)** — labeled map of every Phase 2 screenshot
