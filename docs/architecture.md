# Architecture

## Machines

Mac 1 → Private DNS
Mac 2 → Nginx Edge / Load Balancer
Mac 3 → Backend A
Mac 4 → Backend B

## Request Flow

Client
→ DNS Query
→ DNS Response
→ TCP Connection
→ TLS Handshake
→ HTTPS Request
→ Nginx
→ Backend A/B
→ Response