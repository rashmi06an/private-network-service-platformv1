# Private Network Service Platform

Computer Networks Course Project — **Phase 1: Build & Observe** (Team 1)

A fully local private network service on four macOS laptops: a client types a
private domain (`app.team1.test`), it resolves through the team DNS server,
connects over HTTPS to an nginx reverse proxy, and is load-balanced to one of
two backend services — with packet evidence of the full DNS → TCP → TLS → HTTP flow.

## Team

| Name              | Enrollment No. | Role (Machine)                      |
|-------------------|----------------|-------------------------------------|
| Rashmi Anand      | 2401010374     | Private DNS + Test Client (Mac 1)   |
| Samiksha Jangid   | 2401010410     | Edge: nginx + HTTPS/TLS + LB (Mac 2)|
| Shubhaang Kataruka| 2401010450     | Backend A (Mac 3)                   |
| Ankit Raj Singh   | 2401010075     | Backend B + Test Client (Mac 4)     |

## Architecture

```
Client → Private DNS (Mac 1) → nginx edge/TLS/LB (Mac 2) → Backend A (Mac 3) / Backend B (Mac 4)
```

Full topology, request flow, and OSI/TCP-IP layer mapping: see [docs/architecture.md](docs/architecture.md).

## Repository structure

```
backend-a/     Flask REST backend A  (:3001, X-Backend: A)
backend-b/     Flask REST backend B  (:3002, X-Backend: B)
dns/           dnsmasq config + client resolver setup
edge/          nginx reverse proxy / load balancer + TLS config
scripts/       test scripts: DNS, backends, HTTPS, load balancing
docs/          architecture, network inventory, viva notes
reports/       Phase 1 report
evidence/      screenshots & captures per layer:
               network/ dns/ backends/ nginx/ tls/ caching/ wireshark/ failures/
```

## Run a backend

```bash
cd backend-a            # or backend-b
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
python3 app.py          # A -> :3001, B -> :3002
```

## Verify (from a client Mac)

```bash
scripts/test-dns.sh                      # dig app.team1.test / api.team1.test
scripts/test-backends.sh <MAC3_IP> <MAC4_IP>
scripts/test-https.sh                    # HTTPS + caching headers
scripts/test-load-balancing.sh           # X-Backend alternates A/B
```

## Phase 1 tasks

| Task | What it proves                              | Where                         |
|------|---------------------------------------------|-------------------------------|
| A    | Private LAN + topology + ping               | docs/, evidence/network/      |
| B    | Private DNS (dnsmasq) + client resolvers    | dns/, evidence/dns/           |
| C    | Two REST backends (A/B)                     | backend-a/, backend-b/        |
| D    | nginx reverse proxy + round-robin LB        | edge/, evidence/nginx/        |
| E    | HTTPS / TLS termination                     | edge/, evidence/tls/          |
| F    | HTTP caching (Cache-Control / 304)          | evidence/caching/             |
| G    | Wireshark capture of DNS / TCP / TLS        | evidence/wireshark/           |

See [reports/phase1-report.md](reports/phase1-report.md) for the status checklist,
and [docs/demo-runbook.md](docs/demo-runbook.md) for the live demo commands (11 steps).
