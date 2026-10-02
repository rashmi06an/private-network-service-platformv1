# Phase 1 Report — Team 1

Private Network Service Platform · Build & Observe

## 1. Summary

A complete local service reachable through the private domain
`https://app.team1.test`, demonstrating the full DNS → TCP → TLS → HTTP flow
with load balancing across two backends, all on four macOS laptops on one LAN.

## 2. Task checklist (Review 1)

| Task | Description                                 | Status | Evidence location                |
|------|---------------------------------------------|--------|----------------------------------|
| A    | Private LAN + topology + ping               | TODO   | `evidence/network/`       |
| B    | Private DNS (dnsmasq) + client resolvers    | TODO   | `evidence/dns/`           |
| C    | Two REST backends (A :3001, B :3002)        | TODO   | `evidence/backends/`      |
| D    | nginx reverse proxy + round-robin LB        | TODO   | `evidence/nginx/`         |
| E    | HTTPS / TLS termination at the edge         | TODO   | `evidence/tls/`           |
| F    | HTTP caching (Cache-Control / 304)          | TODO   | `evidence/caching/`       |
| G    | Wireshark capture of DNS / TCP / TLS        | TODO   | `evidence/wireshark/`     |

## 3. Network inventory

See `docs/network-inventory.md` (fill in real IPs, gateway, interface, MAC).

## 4. Configuration bundle

- DNS: `dns/dnsmasq.conf.example`, `dns/client-dns-setup.md`
- Edge: `edge/nginx.conf.example`, `edge/tls.conf.example`
- Backends: `backend-a/`, `backend-b/`
- Test scripts: `scripts/`

## 5. Required failure demonstrations (Section 6.3)

| Scenario                          | Expected observation                                  | Status |
|-----------------------------------|-------------------------------------------------------|--------|
| Wrong DNS server on client        | Name lookup fails though IP connectivity still works  | TODO   |
| DNS record points to wrong IP     | Resolves fine but reaches the wrong destination       | TODO   |
| One backend stopped               | Edge keeps serving via the remaining backend          | TODO   |
| Both backends stopped             | Edge returns 502 Bad Gateway; TLS/DNS still work      | TODO   |
| Wrong destination port on client  | Host reachable but TCP connection to the port fails   | TODO   |

## 6. Learning summary

_(One short paragraph: what the DNS → TCP → TLS → HTTP trace taught the team.)_
