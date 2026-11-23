# Final integrated demonstration — all 11 steps

Use [member commands](team-commands.md) to prepare first. Current addresses:
DNS .27.145, edge .25.25, A .28.78, B/backup DNS .27.247 (all start 10.7).
Keep the actual transcripts/capture files in [evidence](../evidence/README.md).

1. **Topology/inventory:** show [architecture](architecture.md), printable PDF,
   roles/IP/MAC/interface/gateway table and protocol flow. Mark historical IPs.
2. **LAN:** each of four Macs runs its role's `preflight.sh`; show all 12 directed
   ping results and the current IP fields. Explain any measured ICMP restriction.
3. **DNS:** from Mac 2 and Mac 3 show scoped resolver settings, direct primary/
   backup answers and `dscacheutil -q host -a name app.team1.test`.
4. **Trusted HTTPS:** client runs `/usr/bin/curl --noproxy '*' -v
   https://app.team1.test:8443/api/status`; show successful certificate validation,
   domain SAN, TLS protocol and 200. No -k or IP URL.
5. **Load balancing:** Mac 2 runs `scripts/test-load-balancing.sh`; show A/B with
   HTTP 200. Shared upstream state supports round robin; concurrent requests can
   affect the exact observed order.
6. **Packet evidence:** open the saved pcapng listed in [capture guide](packet-evidence.md).
   Identify matching DNS transaction, TCP SYN/SYN-ACK/ACK and ports, TLS
   ClientHello/ServerHello/Certificate, ChangeCipherSpec and encrypted data.
   Explain TLS 1.3 versus the controlled visible-certificate TLS 1.2 trace.
7. **Caching:** `scripts/test-https.sh` uses /api/cache-demo and asserts an actual
   304 through the same trusted hostname. Explain fresh hit, conditional
   validation, full response, and why both backends share this representation.
8. **Backend failure/recovery:** `test-ha-failover.sh balanced`, stop only A,
   `test-ha-failover.sh a-down`, restart A, wait 11s, `test-ha-failover.sh recovered`.
9. **Phase 2 resilience:** show primary-DNS outage with fresh client lookup;
   timed TTL expiry; separate manual flush; edge/client isolation plus rollback;
   synchronized standby cutover and cache effects. These are all mandatory
   extensions even if the evaluator asks for a shorter selection at this step.
10. **Faculty fault:** narrate DNS → TCP → TLS → edge HTTP → backend. Check both
    DNS servers AND actual system lookup. Run backend direct curls from Mac 2,
    since a denied client is expected to time out while isolation is active.
    Identify/fix or isolate the fault and record the actual outcome afterwards.
11. **Individual viva:** every member explains any layer and extension without
    reading notes. [Viva notes](viva-notes.md) are for rehearsal, not answers to read.

## Role-aware diagnosis commands

Client (Mac 1/2/3/4):

```bash
dig @10.7.27.145 app.team1.test
dig @10.7.27.247 app.team1.test
dscacheutil -q host -a name app.team1.test
nc -vz -w 3 10.7.25.25 8443
/usr/bin/curl --noproxy '*' --connect-timeout 3 --max-time 10 -vI https://app.team1.test:8443/
```

Permitted primary edge **Mac 2**, with both backends expected up:

```bash
scripts/test-backends.sh
```

DNS failure means no usable name answer; TCP failure means no usable socket;
TLS failure means transport works but identity/trust/handshake fails; 502 at a
trusted reachable edge points to its upstream path. DNS may still resolve during
an application outage. Confirm a hypothesis with the correct host and firewall state.
