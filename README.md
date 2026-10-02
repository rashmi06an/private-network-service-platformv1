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

### Protocol flow — what each capture shows (Task G)

A single `https://app.team1.test:8443/api/status` request, captured and explained layer by layer:

| Layer / Event | What we show and explain | Evidence |
|---------------|--------------------------|----------|
| DNS | Client query for `app.team1.test` and the response containing Mac 2's IP (`10.7.7.9`), over UDP/53. | `evidence/wireshark/wireshark-dns.png` |
| TCP handshake | `SYN -> SYN-ACK -> ACK` before any application data; source + destination ports recorded. | `evidence/wireshark/tcp-syn-detail.png` |
| TLS handshake | `ClientHello`, `ServerHello`, `Certificate`, `ChangeCipherSpec`; after this only encrypted Application Data. | `evidence/wireshark/tls-client-hello.png` |
| HTTP headers | Request/response headers via `curl -v`; payload is unreadable in Wireshark because it's encrypted inside TLS. | `evidence/tls/https-by-name.png` |
| Load balancing | Repeated requests served by both Backend A and Backend B (visible in `X-Backend`). | `evidence/nginx/domain-load-balancing.txt` |
| Port identification | Client ephemeral source port -> server well-known port: **53/UDP** (DNS), **8443/TCP** (HTTPS). | `evidence/wireshark/tcp-tls-full-exchange.png` |

### Failure demonstrations (Section 6.3)

Each failure was injected deliberately, observed, and then restored:

| Scenario | Expected observation and explanation | Evidence |
|----------|--------------------------------------|----------|
| Wrong DNS server on a client | Name lookup fails (NXDOMAIN) even though the IP is still reachable — DNS and IP layers are independent. | `evidence/failures/wrong-dns-server.png` |
| DNS record points to a wrong IP | Resolution succeeds but the client reaches the wrong destination — DNS is a directory, not a connection. | `evidence/failures/wrong-dns-record.png` |
| One backend stopped | The edge keeps serving through the remaining backend (all `X-Backend: B`). | `evidence/failures/backend-a-down.png` |
| Both backends stopped | DNS and TLS still work at the edge, but nginx returns `502 Bad Gateway` — shows where the edge ends and the backend begins. | `evidence/failures/both-down-502.png` |
| Wrong destination port | Host is reachable but the TCP connection to the port fails — ports and IP addresses are separate identifiers. | `evidence/failures/wrong-port.png` |

---

## Course-topic mapping (OSI vs TCP/IP)

| Course topic | Where it appears in this project |
|--------------|----------------------------------|
| Moving data through the core | Client request crosses the LAN to the edge and back — captured in Wireshark. |
| OSI vs TCP/IP model | DNS/HTTP = Application · TLS = Session/Transport · TCP/UDP = Transport · IP = Network · Ethernet = Link. |
| Devices, topologies, cloud concepts | Local topology (Mac 1–4) mapped to cloud roles (Route 53, cloud LB, app instances). |
| HTTP/1.1, HTTP/2, REST | REST API on both backends; HTTP/1.1 demonstrated (HTTP/2 enabled on the edge). |
| HTTPS and TLS | TLS terminated at nginx; handshake + certificate validation captured. |
| Transport layer, ports, TCP/UDP | Service ports and the TCP three-way handshake identified in the capture. |
| Reliable data transfer, TCP flow control | Sequence/acknowledgement numbers shown in the handshake. |
| Caching | `Cache-Control` + `ETag` with a `304 Not Modified` conditional request. |
| Cloud load balancing | nginx round-robin across two backends (relates to AWS ALB / GCP LB). |
| DNS and Route 53 concepts | Private `app.team1.test` zone with two client machines resolving through Mac 1. |

---

## Key documents

- **[reports/phase1-report.md](reports/phase1-report.md)** — full Phase 1 report + results
- **[docs/demo-runbook.md](docs/demo-runbook.md)** — live demo commands (11 steps)
- **[docs/architecture.md](docs/architecture.md)** — topology, request flow, layer mapping
- **[docs/network-inventory.md](docs/network-inventory.md)** — IP / MAC / service tables
