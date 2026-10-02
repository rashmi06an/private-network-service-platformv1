# Private Network Service Platform

Computer Networks Course — Phase 1

## Team Members

| Name | Enrollment No. | Role |
|---|---|---|
| Rashmi Anand | 2401010374 | Private DNS + Test Client |
| Samiksha Jangid | 2401010410 | Nginx + HTTPS/TLS |
| Shubhaang Kataruka | 2401010450 | Backend A |
| Ankit Raj Singh | 2401010075 | Backend B |

## Architecture

Client
→ Private DNS
→ Nginx Reverse Proxy
→ Backend A / Backend B

## Infrastructure

macOS laptops on the same private LAN.

## Services

- Private DNS: dnsmasq
- Reverse Proxy / Load Balancer: nginx
- Backend A: HTTP :3001
- Backend B: HTTP :3002
- HTTPS: TLS terminated at nginx

## Domain

app.team1.test

## Phase 1

The project demonstrates:

- Private DNS
- TCP connectivity
- HTTP/REST
- Reverse proxy
- Load balancing
- HTTPS/TLS
- HTTP caching
- Wireshark packet analysis
- Failure diagnosis