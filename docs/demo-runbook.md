# Phase 1 Demo Runbook — Team 1

Exact commands for the live demonstration (Section 8, 11 steps), using the real
Team 1 LAN addresses. Ports assume `443`; if you bound nginx to `8443`, append
`:8443` to the HTTPS URLs.

## Addresses

| Host  | Role        | IP           | Port       |
|-------|-------------|--------------|------------|
| Mac 1 | DNS + client| `10.7.17.21` | 53/UDP     |
| Mac 2 | nginx edge  | `10.7.7.9`   | 443 (HTTPS)|
| Mac 3 | Backend A   | `10.7.7.17`  | 3001       |
| Mac 4 | Backend B   | `10.7.23.47` | 3002       |

Domain: `app.team1.test`, `api.team1.test` → `10.7.7.9`

---

## Pre-demo startup (do before the evaluator arrives)

**Mac 3 — Backend A**
```bash
cd backend-a && source venv/bin/activate && python3 app.py   # listens on 0.0.0.0:3001
```
**Mac 4 — Backend B**
```bash
cd backend-b && source venv/bin/activate && python3 app.py   # listens on 0.0.0.0:3002
```
**Mac 1 — DNS**
```bash
sudo brew services start dnsmasq      # or: sudo dnsmasq -C /opt/homebrew/etc/dnsmasq.conf
```
**Mac 2 — nginx**
```bash
sudo nginx -t && sudo nginx           # or: sudo nginx -s reload
```
**Clients (Mac 1 & Mac 4):** DNS resolver set to `10.7.17.21`, local CA trusted (mkcert).

---

## The 11 demonstration steps

### 1. Topology and IP/service inventory
Show `docs/architecture.md` (diagram + layer map) and `docs/network-inventory.md`
(IP/MAC/service tables).

### 2. All machines on the private LAN
```bash
ping -c 2 10.7.17.21    # Mac 1
ping -c 2 10.7.7.9      # Mac 2
ping -c 2 10.7.7.17     # Mac 3
ping -c 2 10.7.23.47    # Mac 4
```

### 3. Resolve the private domain from a client
```bash
dig app.team1.test
dig api.team1.test
# Expect: ANSWER section shows 10.7.7.9, SERVER: 10.7.17.21#53
```

### 4. Open the service over HTTPS by name (no cert warning, no IP in URL)
```bash
curl -v https://app.team1.test/api/status      # note: NO -k flag
# In a browser: https://app.team1.test  -> padlock, no warning
```

### 5. Load balancing across both backends
```bash
for i in $(seq 1 8); do
  curl -s -D - https://app.team1.test/api/status -o /dev/null | grep -i x-backend
done
# Expect: X-Backend alternates A / B  (round-robin)
```

### 6. Wireshark evidence of DNS, TCP, TLS
Open the saved capture in `evidence/wireshark/`. Point to:
- DNS query/response for `app.team1.test` (53/UDP)
- TCP `SYN → SYN-ACK → ACK` (443/TCP)
- TLS `ClientHello → ServerHello → Certificate`
- `Application Data` frames (payload encrypted)

### 7. HTTP headers and caching
```bash
curl -I https://app.team1.test/api/status            # show Cache-Control: max-age=60 + ETag
ETAG=$(curl -sI https://app.team1.test/api/status | awk -F': ' 'tolower($1)=="etag"{print $2}' | tr -d '\r')
curl -s -o /dev/null -w "%{http_code}\n" -H "If-None-Match: $ETAG" https://app.team1.test/api/status
# Expect: 304 Not Modified
```

### 8. Fail one backend, prove service continues
```bash
# On Mac 3: stop Backend A (Ctrl-C), then from a client:
for i in $(seq 1 6); do
  curl -s -D - https://app.team1.test/api/status -o /dev/null | grep -i x-backend
done
# Expect: all responses now X-Backend: B  (service stays up)
```

### 9. Phase 2 resilience (if showing) — skip for Phase 1-only review
Backup DNS failover / TTL / DNS cutover (Extensions A/B/E).

### 10. Faculty-injected fault — diagnose layer by layer
Order of checks: DNS → TCP → TLS → application.
```bash
dig app.team1.test                      # DNS layer OK?
nc -vz 10.7.7.9 443                      # TCP to edge OK?
curl -vI https://app.team1.test/         # TLS/HTTP OK?
curl -s http://10.7.7.17:3001/api/status # backend A directly
curl -s http://10.7.23.47:3002/api/status# backend B directly
```

### 11. Individual viva
Each member explains any component — see `docs/viva-notes.md`.

---

## Quick layer-isolation cheatsheet (for step 10)

| Symptom                                   | Likely layer | Check                                  |
|-------------------------------------------|--------------|----------------------------------------|
| Name won't resolve                        | DNS          | `dig`, resolver = `10.7.17.21`         |
| Resolves but connection refused/timeout   | TCP/port     | `nc -vz 10.7.7.9 443`                  |
| Connects but cert error                   | TLS          | `curl -vI`, CA trusted on client?      |
| 502 Bad Gateway                           | Backend/app  | curl backends directly on :3001/:3002  |
| Wrong/old IP returned                     | DNS record   | check `dnsmasq.conf` address lines     |
