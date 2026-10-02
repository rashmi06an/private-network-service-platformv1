# Private Network Service Platform

> **Computer Networks — Course Project · Phase 1: Build & Observe · Team 1**
> Status: **Phase 1 complete** — all build tasks, failure demonstrations, and packet evidence collected.

A fully **local** private network service running on four macOS laptops — no cloud,
no pre-configured servers. A client types a private domain
(`https://app.team1.test:8443`); the name resolves through our own DNS server,
connects over HTTPS to an nginx reverse proxy, and is load-balanced to one of two
backend services — and every protocol layer is captured in Wireshark.

```
Client -> Private DNS (Mac 1) -> nginx edge, TLS, load balancer (Mac 2) -> Backend A (Mac 3) / Backend B (Mac 4)
```

---

## Team

| Name | Enrollment No. | Role | Machine |
|------|----------------|------|---------|
| Rashmi Anand | 2401010374 | Private DNS (dnsmasq) + Test Client | Mac 1 |
| Samiksha Jangid | 2401010410 | nginx Edge — HTTPS/TLS + Load Balancer | Mac 2 |
| Shubhaang Kataruka | 2401010450 | Backend A (Flask REST) | Mac 3 |
| Ankit Raj Singh | 2401010075 | Backend B (Flask REST) + Test Client | Mac 4 |

---

## Topology

![Network topology diagram](evidence/network/topology-diagram.png)

All four Macs share one private Wi-Fi/LAN (`10.7.0.0/19`, gateway `10.7.0.1`).

| Machine | Role | Address | Cloud equivalent |
|---------|------|---------|------------------|
| Mac 1 | Private DNS (dnsmasq) + client | `10.7.17.21:53` | Managed DNS (Route 53) |
| Mac 2 | nginx edge: TLS + load balancer | `10.7.7.9:8443` | Cloud load balancer / CDN |
| Mac 3 | Backend A (REST) | `10.7.21.15:3001` | App server instance A |
| Mac 4 | Backend B (REST) | `10.7.23.47:3002` | App server instance B |

**Domain:** `app.team1.test` and `api.team1.test` resolve to `10.7.7.9` (Mac 2).

---

## Architecture — one request, layer by layer

```
Client (Mac 1 / Mac 4)
  | 1. DNS QUERY     -- UDP 53   -->  Mac 1 (dnsmasq)   "app.team1.test = ?"  -> 10.7.7.9
  | 2. TCP HANDSHAKE -- TCP 8443 -->  Mac 2   SYN -> SYN-ACK -> ACK
  | 3. TLS HANDSHAKE -->              Mac 2   ClientHello -> ServerHello -> Certificate -> Finished
  | 4. HTTPS REQUEST -->              Mac 2   GET /api/status   (payload now encrypted)
  v
Mac 2  nginx reverse proxy + round-robin load balancer
  |--> Mac 3  Backend A :3001   (X-Backend: A)
  |--> Mac 4  Backend B :3002   (X-Backend: B)
```

| Layer | Protocol | Port |
|-------|----------|------|
| Application | DNS / HTTP(S) | 53/UDP, 8443/TCP |
| Session/Transport | TLS | 8443/TCP |
| Transport | TCP | 8443/TCP, 3001/3002 |
| Network / Link | IP / Ethernet | — |

Full diagram, OSI/TCP-IP mapping, and explanation: **[docs/architecture.md](docs/architecture.md)**.

---

## Repository structure

```
backend-a/     Flask backend A  — /, /api/status, /api/cache-demo   (:3001, X-Backend: A)
backend-b/     Flask backend B  — same endpoints                    (:3002, X-Backend: B)
dns/           dnsmasq config + client resolver setup
edge/          nginx reverse proxy / load balancer + TLS config
scripts/       test scripts: DNS, backends, HTTPS, load balancing
docs/          architecture (+ topology diagram), network inventory, demo runbook
reports/       Phase 1 report
evidence/      screenshots & captures, one folder per layer:
               network/  dns/  backends/  nginx/  tls/  caching/  wireshark/  failures/
```

---

## Run

**Backends (Mac 3 and Mac 4):**
```bash
cd backend-a            # or backend-b on Mac 4
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
python3 app.py          # A -> 0.0.0.0:3001 ,  B -> 0.0.0.0:3002
```

**DNS (Mac 1):** `sudo brew services start dnsmasq` (config: [dns/dnsmasq.conf.example](dns/dnsmasq.conf.example))
**Edge (Mac 2):** `sudo nginx -t && sudo nginx` (config: [edge/nginx.conf.example](edge/nginx.conf.example), [edge/tls.conf.example](edge/tls.conf.example))

---

## Verify (from a client)

```bash
scripts/test-dns.sh               # resolves app/api.team1.test via Mac 1
scripts/test-backends.sh          # both backends answer (defaults to real IPs)
scripts/test-https.sh             # HTTPS + Cache-Control headers
scripts/test-load-balancing.sh    # X-Backend alternates A / B
```

---

## Phase 1 tasks — all complete

| Task | What it proves | Evidence |
|------|----------------|----------|
| A | Private LAN + topology + ping | [evidence/network/](evidence/network/) |
| B | Private DNS + two client resolvers | [evidence/dns/](evidence/dns/) |
| C | Two REST backends, `X-Backend` header | [evidence/backends/](evidence/backends/) |
| D | nginx round-robin load balancing | [evidence/nginx/](evidence/nginx/) |
| E | HTTPS / TLS termination (trusted cert) | [evidence/tls/](evidence/tls/) |
| F | HTTP caching (Cache-Control + 304) | [evidence/caching/](evidence/caching/) |
| G | Wireshark: DNS, TCP, TLS, encrypted data | [evidence/wireshark/](evidence/wireshark/) |

**Failure demonstrations (Section 6.3)** — wrong DNS server, wrong DNS record,
one backend down, both backends down (502), wrong port -> [evidence/failures/](evidence/failures/)

---

## Key documents

- **[reports/phase1-report.md](reports/phase1-report.md)** — full Phase 1 report + results
- **[docs/demo-runbook.md](docs/demo-runbook.md)** — live demo commands (11 steps)
- **[docs/architecture.md](docs/architecture.md)** — topology, request flow, layer mapping
- **[docs/network-inventory.md](docs/network-inventory.md)** — IP / MAC / service tables
