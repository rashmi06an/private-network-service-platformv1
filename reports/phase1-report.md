# Phase 1 Report — Team 1

**Private Network Service Platform · Build & Observe**

## 1. What we built

A fully local private service, running only on four MacBooks on the same Wi-Fi —
no cloud. A client types **`https://app.team1.test:8443`**, and the request travels:

```
Client → Private DNS (Mac 1) → nginx HTTPS edge (Mac 2) → Backend A (Mac 3) / Backend B (Mac 4)
```

Everything works end to end: the name resolves through our own DNS, connects over
HTTPS with a trusted certificate, and is load-balanced across two backend servers —
and we captured every protocol layer in Wireshark.

## 2. The team and machines

| Machine | Member | Role | Address |
|---------|--------|------|---------|
| Mac 1 | Rashmi | Private DNS (dnsmasq) + test client | `10.7.17.21:53` |
| Mac 2 | Samiksha | nginx edge: HTTPS/TLS + load balancer | `10.7.7.9:8443` |
| Mac 3 | Shubhaang | Backend A (Flask REST) | `10.7.21.15:3001` |
| Mac 4 | Ankit | Backend B (Flask REST) | `10.7.23.47:3002` |

Domain: `app.team1.test` and `api.team1.test` → `10.7.7.9` (Mac 2).
Full details in [docs/network-inventory.md](../docs/network-inventory.md) and
[docs/architecture.md](../docs/architecture.md).

## 3. Build tasks — all complete ✅

| Task | What it shows | Status | Evidence |
|------|---------------|--------|----------|
| A | Private LAN + ping between all Macs | ✅ | `evidence/network/mac1-ifconfig-ping.png` |
| B | Private DNS resolves our domain; clients use Mac 1 | ✅ | `evidence/dns/` (dig, dnsmasq, Mac 3 & Mac 4 clients) |
| C | Two REST backends, `X-Backend: A/B` header | ✅ | `evidence/backends/` (status + listening) |
| D | nginx round-robin load balancing | ✅ | `evidence/nginx/` (X-Backend alternates A/B) |
| E | HTTPS with a trusted cert (no `-k`) | ✅ | `evidence/tls/https-by-name.png` |
| F | HTTP caching: `Cache-Control` + `304` | ✅ | `evidence/caching/` (headers + 304) |
| G | Wireshark: DNS, TCP, TLS, encrypted data | ✅ | `evidence/wireshark/` (DNS, SYN, handshake, Client Hello) |

## 4. Failure demonstrations — all complete ✅

We deliberately broke the system to prove we understand each layer.

| # | We broke... | What happened | Evidence |
|---|-------------|---------------|----------|
| 1 | Wrong DNS server (queried `8.8.8.8`) | `NXDOMAIN` — name fails, but IP still pings | `wrong-dns-server.png` |
| 2 | DNS record → wrong IP (`10.7.7.250`) | Resolves fine, but connection times out (wrong place) | `wrong-dns-record.png` |
| 3 | Stopped the DNS server | Lookup fails; IP still reachable (service ≠ network) | `dns-unavailable.png` |
| 4 | Stopped Backend A | Service continues — all requests served by Backend B | `backend-a-down.png` |
| 5 | Stopped both backends | nginx returns `502 Bad Gateway` (edge up, backends down) | `both-down-502.png` |
| 6 | Wrong port (`:9999`) | Host reachable, but TCP connection refused | `wrong-port.png` |

After each test we restored the known-good setup (see the `*-restored.png` and
`recovery-after-restart.png` screenshots).

## 5. The key idea (for the viva)

A single request uses **different layers that are independent of each other**:

- **DNS** is just a directory — it maps the name to an IP (`10.7.7.9`) over UDP/53.
  It does **not** make the connection.
- **TCP** then opens the connection (SYN → SYN-ACK → ACK) to the edge on port 8443.
- **TLS** secures it (ClientHello → ServerHello → Certificate → Finished); after
  this, the HTTP data is **encrypted** (Wireshark shows only "Application Data").
- **HTTP** finally carries the request; nginx load-balances it to Backend A or B.

This is why our failure tests make sense: DNS can break while the network is fine,
a backend can die while the edge stays up, and a wrong port fails even when the
host is reachable — each layer can fail on its own.

## 6. Configuration bundle

- DNS: [dns/dnsmasq.conf.example](../dns/dnsmasq.conf.example), [dns/client-dns-setup.md](../dns/client-dns-setup.md)
- Edge: [edge/nginx.conf.example](../edge/nginx.conf.example), [edge/tls.conf.example](../edge/tls.conf.example)
- Backends: [backend-a/](../backend-a/), [backend-b/](../backend-b/)
- Test scripts: [scripts/](../scripts/)
