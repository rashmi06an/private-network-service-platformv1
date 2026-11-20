# Phase 2 observations — from team-shared Mac terminal logs, 20 Nov 2026

These are **actual reported terminal outputs**, condensed without inventing tests. This file is not a substitute for timestamped screenshots or the final faculty-injected fault challenge.

## A — Backup DNS

Mac 3 direct client checks: primary (`10.7.27.145`) and backup (`10.7.27.247`) both returned `10.7.25.25`. Mac 4 DNS listened on UDP/TCP port 53, and logs recorded A record queries for `app.team1.test` from `10.7.28.78` and `10.7.25.25`, returning `10.7.25.25` at the time. Mac 2 and 3 `dscacheutil` resolved `app.team1.test` to `10.7.25.25`, and HTTPS returned HTTP 200. Primary DNS stop and restart are logged, but the exact simultaneous timing of outage and backup client usage is not independently established by the supplied excerpts.

## B — DNS TTL

Verified TTL:

```text
ttl.team1.test.  30  IN  A  10.7.25.25
```

During record change, Mac 3 observed:

```text
=== CURRENT SERVER ANSWER ===
10.7.28.78
=== CLIENT CACHED ANSWER ===
name: ttl.team1.test
ip_address: 10.7.25.25
```

After a 35-second wait:

```text
ttl.team1.test.  30  IN  A  10.7.28.78
name: ttl.team1.test
ip_address: 10.7.28.78
```

Manual flush **not yet proven**: the provided before/after outputs were both 10.7.25.25. It may have expired before flushing.

## C — Backend PF firewall isolation

Mac 3 loaded a PF allow rule from 10.7.25.25 and deny rule for other sources to port 3001. Mac 4 loaded the corresponding rules for port 3002. Mac 2 could directly GET both HTTP backends (`200 OK` with X-Backend A/B). During isolation, Mac 1 received:

```text
=== BACKEND A MUST BE BLOCKED ===
curl: (28) Failed to connect to 10.7.28.78 port 3001 after 3004 ms: Timeout was reached
=== BACKEND B MUST BE BLOCKED ===
curl: (28) Failed to connect to 10.7.27.247 port 3002 after 3006 ms: Timeout was reached
```

After rollback Mac 1 directly reached both backends with JSON `status: ok`. Mac 3 cleared its test anchor and released its PF reference; Mac 4 cleared its test anchor and released its PF reference. **PASS for controlled isolation and rollback.**

## D — Backend A failure and recovery

Mac 2 observed 10 successive requests while Backend A was down, all as:

```text
HTTP/1.1 200 OK
X-Backend: B
```

After Backend A restarted, a 10-request sample showed HTTP 200 from both `X-Backend: A` and `X-Backend: B`. **PASS for observed backend failover and recovery.** This does not imply primary nginx edge has automatic HA.

## E — Standby nginx and DNS cutover

Mac 3's standby nginx syntax test passed and it listened on TCP 8443. The transferred leaf TLS certificate file was valid from 2 Oct 2026 through 2 Jan 2029. The operator reported successful HTTPS-by-standby, DNS change and restoration. **Independent E1–E4 output was not included in the supplied excerpts**, so retain screenshots before certifying full cutover.

**Restoration warning from Mac 3 log at 20:25:51 IST:**

```text
;; SERVER: 10.7.27.145#53
app.team1.test. 30 IN A 10.7.25.25
;; SERVER: 10.7.27.247#53
app.team1.test. 0 IN A 10.7.28.78
```

Both DNS servers must point to `10.7.25.25` during normal operation. This mismatch must be corrected on Mac 4 (possibly a foreground dnsmasq instance running an old config), **and the final state rechecked** before submission.

## F — Faculty troubleshooting

Phase 1 screenshots document deliberate DNS, port, backend, and edge failures. The real faculty-injected fault happens during evaluation and cannot be declared passed beforehand. Diagnosis order: DNS → TCP → TLS → HTTP/application.
