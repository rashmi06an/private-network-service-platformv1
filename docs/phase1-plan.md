# Phase 1 Checklist

## Task A — LAN

- [ ] All 4 Macs connected to same LAN
- [ ] IP addresses recorded
- [ ] Subnet recorded
- [ ] Gateway recorded
- [ ] Interface recorded
- [ ] MAC addresses recorded
- [ ] All-to-all ping successful
- [ ] Topology diagram complete

## Task B — DNS

- [ ] dnsmasq installed
- [ ] Private domain configured
- [ ] app.team1.test configured
- [ ] api.team1.test configured
- [ ] Client DNS configured
- [ ] dig verified

## Task C — Backends

- [ ] Backend A running on :3001
- [ ] Backend B running on :3002
- [ ] GET /
- [ ] GET /api/status
- [ ] X-Backend header

## Task D — Edge

- [ ] nginx installed
- [ ] Reverse proxy configured
- [ ] Load balancing configured
- [ ] A/B responses verified

## Task E — TLS

- [ ] Certificate created
- [ ] Certificate trusted by clients
- [ ] HTTPS working
- [ ] curl works without -k
- [ ] TLS handshake captured

## Task F — Caching

- [ ] Cache-Control header
- [ ] Cache behavior demonstrated

## Task G — Packet Analysis

- [ ] DNS query/response
- [ ] TCP SYN
- [ ] TCP SYN-ACK
- [ ] TCP ACK
- [ ] TLS handshake
- [ ] Encrypted application data
- [ ] Ports identified

## Failure Demonstrations

- [ ] Wrong DNS server
- [ ] Wrong DNS record
- [ ] Backend A stopped
- [ ] Both backends stopped
- [ ] Wrong destination port