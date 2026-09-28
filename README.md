# Private Network Service Platform

A fully local team-based networking project demonstrating:

- Private DNS
- TCP
- HTTPS / TLS
- HTTP/REST
- Reverse Proxy
- Load Balancing
- HTTP Caching
- Wireshark Packet Analysis

## Architecture

Client
↓
Private DNS
↓
Nginx Edge
↓
Backend A / Backend B

## Machine Roles

| Machine | Role | Service |
|---|---|---|
| Mac 1 | DNS + Client | dnsmasq |
| Mac 2 | Edge | nginx |
| Mac 3 | Backend A | HTTP :3001 |
| Mac 4 | Backend B + Client | HTTP :3002 |

## Domain

app.team1.test
api.team1.test

## Phase 1

- [ ] LAN connectivity
- [ ] Private DNS
- [ ] Backend A
- [ ] Backend B
- [ ] nginx reverse proxy
- [ ] Load balancing
- [ ] HTTPS/TLS
- [ ] HTTP caching
- [ ] Wireshark analysis
- [ ] Failure demonstrations

## Phase 2

To be implemented after Phase 1.

## Team

| Member | Machine | Primary Role |
|---|---|---|
| Member 1 | Mac 1 | DNS |
| Member 2 | Mac 2 | Edge |
| Member 3 | Mac 3 | Backend A |
| Member 4 | Mac 4 | Backend B |