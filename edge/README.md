# Edge — Mac 2 (nginx)

Mac 2 is the **single entry point** for the whole service. Clients never talk to the
backends directly — every request goes through this nginx edge, which does three jobs:

1. **TLS termination (HTTPS)** — serves `https://app.team1.test:8443` using an mkcert
   certificate; TLS is decrypted here, then plain HTTP is forwarded to the backends.
2. **Reverse proxy** — hides the backend IPs; clients only ever see the edge.
3. **Load balancer** — round-robin across Backend A (`10.7.21.15:3001`) and
   Backend B (`10.7.23.47:3002`); the backend that served each request is visible in
   the `X-Backend: A|B` response header.

## Ports

| Port | Purpose |
|------|---------|
| 8080 | HTTP → redirects to HTTPS |
| 8443 | HTTPS (TLS terminated here) |

> We use `8080/8443` instead of `80/443` because binding to privileged ports isn't
> required (allowed by the project rules — no marks deducted).

## Files

- [nginx.conf.example](nginx.conf.example) — reverse proxy, round-robin upstream,
  HTTP→HTTPS redirect, and `Cache-Control` on `/api/status`.
- [tls.conf.example](tls.conf.example) — TLS settings + certificate paths, with
  mkcert/OpenSSL generation and client-trust instructions.

> These are `.example` files. Copy them into your real nginx config location
> (e.g. `/opt/homebrew/etc/nginx/`) and adjust the certificate paths. Do **not**
> commit the machine-specific live `nginx.conf`.

## Apply / reload

```bash
sudo nginx -t          # test config
sudo nginx             # start  (or: sudo nginx -s reload to apply changes)
```

## Verify (from a client)

```bash
# HTTPS works by name, trusted cert (no -k)
curl -v https://app.team1.test:8443/api/status

# Load balancing — X-Backend alternates A / B
for i in $(seq 1 8); do
  curl -s -D - https://app.team1.test:8443/api/status -o /dev/null | grep -i x-backend
done
```

## TLS handshake (for the viva)

`ClientHello → ServerHello → Certificate → Key Exchange → Finished`.
After the handshake the HTTP payload is encrypted, which is why Wireshark shows only
`Application Data` — use `curl -v` to see the cleartext request/response.
