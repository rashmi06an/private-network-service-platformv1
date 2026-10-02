# Request Flow — One Client Request, Layer by Layer

This traces a single `https://app.team1.test/api/status` request from a client
Mac through every protocol layer, which is exactly what Task G must capture.

```
Client (Mac 1 / Mac 4)
   │
   │ 1. DNS QUERY  ── UDP :53 ──►  Mac 1 (dnsmasq)
   │    "app.team1.test = ?"
   │ ◄── DNS RESPONSE ──           "app.team1.test -> Mac 2 IP"
   │
   │ 2. TCP HANDSHAKE ── TCP :443 ──►  Mac 2 (nginx)
   │    SYN -> SYN-ACK -> ACK
   │
   │ 3. TLS HANDSHAKE ──►  Mac 2 (nginx)
   │    ClientHello -> ServerHello -> Certificate
   │    -> Key Exchange -> Finished        (app data now encrypted)
   │
   │ 4. HTTPS REQUEST ──►  Mac 2 (nginx)
   │    GET /api/status
   ▼
Mac 2  nginx reverse proxy + round-robin load balancer
   │
   ├── 5a. proxy_pass ──► Mac 3  Backend A  :3001   (X-Backend: A)
   └── 5b. proxy_pass ──► Mac 4  Backend B  :3002   (X-Backend: B)
   │
   │ 6. HTTP RESPONSE (JSON + X-Backend + Cache-Control)
   ▼
Client receives response over the encrypted TLS channel
```

## Layer / protocol map (OSI ↔ TCP/IP)

| Step | Protocol        | OSI layer           | Port            |
|------|-----------------|---------------------|-----------------|
| 1    | DNS             | Application         | 53/UDP          |
| 2    | TCP             | Transport           | 443/TCP         |
| 3    | TLS             | Session / Transport | 443/TCP         |
| 4/6  | HTTP/HTTPS      | Application         | 443/TCP         |
| 5    | HTTP (to backend)| Application        | 3001 / 3002 TCP |
|  —   | IP / Ethernet   | Network / Link      | —               |

## Key points to explain in the viva

- **DNS is a directory, not a connection** — it only maps the name to Mac 2's IP;
  the TCP/TLS connection that follows is a separate step.
- The **client never knows the backend IPs**; it only ever talks to the edge (Mac 2).
- After the TLS handshake the HTTP payload is **encrypted**, so Wireshark shows
  `Application Data`, not readable headers — use `curl -v` for the cleartext view.
