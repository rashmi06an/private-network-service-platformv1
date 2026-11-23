# Phase 2 report — Harden, Recover and Troubleshoot

Team Scout Regiment · Current review: 23 November 2026.
The [verification ledger](verification-status.json) records reviewed evidence and
remaining work. The actual faculty challenge and individual viva remain live
assessment tasks; rehearsal does not certify those outcomes.

## System

| Machine | Member | Role | Address |
|---|---|---|---|
| Mac1 | Rashmi | Primary DNS and client | 10.7.27.145:53 |
| Mac2 | Samiksha | Primary HTTPS edge and load balancer | 10.7.25.25:8443 |
| Mac3 | Shubhaang | Backend A and standby edge | 10.7.28.78:3001 / :8443 |
| Mac4 | Ankit | Backend B and backup DNS | 10.7.27.247:3002 / :53 |

Normal app/api/ttl.team1.test records point to Mac2 with TTL30. All four clients
have the two current private resolvers in the scoped team1.test configuration.
The existing public resolver configuration is separate. Mac4's obsolete global
private DNS address was removed and its final readback is8.8.8.8.
See [inventory](../docs/network-inventory.md) and [architecture](../docs/architecture.md).

Phase2 adds synchronized backup DNS, measured TTL experiments, scoped backend
isolation and rollback, explicit passive upstream failure handling, and controlled
standby migration. The applications share cache content and ETag team1-cache-v2,
return no-store on status, support conditional304, and expose backend identity.
Nginx exposes primary/standby identity with X-Edge and uses shared upstream state.
The role-checked detached backend manager avoids dependence on a foreground terminal;
it validates ownership before stopping a process. It is not a reboot service.

## Reviewed results

All times below are UTC on23November. Original recorder files, structured operator
transcriptions and historical screenshots are distinguished in each artifact.

| Requirement | Reviewed outcome and evidence |
|---|---|
| Current inventories / LAN | All four IP/MAC/interface/prefix/gateway inventories supplied. Nine of12 directed ping probes pass; three inbound-to-Mac1 probes fail. Managed Mac1 stealth remains ON and rejects the CLI change. This restriction remains open; DNS/TCP service success does not prove ICMP success. [Observations](../evidence/verification/2026-11-23-three-mac-inventory-observations.json), [policy readback](../evidence/verification/2026-11-23-managed-stealth-and-dns-rechecks.json) |
| Baseline / cache / HTTP2 | Both current backends have correct identity/no-store/shared validator/direct304. Normal hostname HTTPS is trusted and negotiatesHTTP2. Twelve requests returnA6/B6. [Backend check](../evidence/verification/D-recovered-apps-20261123T061004Z.txt), [HTTPS/cache](../evidence/verification/D-recovered-https-20261123T061004Z.txt), [HTTP2](../evidence/verification/R1-http2-recheck-20261123T045545Z.txt) |
| Dual client DNS | Canonical scoped settings verified on all four clients; [Mac2](../evidence/verification/R1-mac2-client-dns-20261123T044808Z.txt), [Mac3](../evidence/verification/R2-mac3-client-dns-20261123T050122Z.txt), [Mac1](../evidence/verification/R2-mac1-client-dns-20261123T050558Z.txt), [Mac4](../evidence/verification/R2-mac4-client-dns-20261123T050617Z.txt) |
| A — Backup DNS | Primary stopped05:15:26–34. Fresh Mac2 lookup and trusted HTTPS200 succeed through the backup; normal resolver transaction38321 is received/replied05:15:51. Primary restored05:16:40–41 and both datasets verified. [Down test](../evidence/verification/A-primary-down-20261123T051545Z.txt), [backup receipt](../evidence/verification/A-backup-receipt-20261123T051432Z.txt), [restored](../evidence/verification/A-restored-20261123T051653Z.txt) |
| B — Natural expiry | Real client cache retains OLD while both authorities serve NEW; TTL declines to1 and NEW appears31.49seconds after priming. Both authorities subsequently restored and checked. [Client log](../evidence/verification/B-expiry-20261123T052539Z.txt), [timeline](../evidence/verification/2026-11-23-ttl-expiry-timeline.json), [final restore check](../evidence/verification/B-expiry-final-restored-20261123T053310Z.txt) |
| B — Separate manual flush | Cache stillOLD/TTL25; explicit owned-cache flush obtains NEW after5.25seconds, before natural30second expiry. Both authorities subsequently restored. [Client log](../evidence/verification/B-manual-flush-20261123T053519Z.txt), [final restore check](../evidence/verification/B-flush-restored-recheck-20261123T054126Z.txt) |
| C — Isolation / rollback | Mac2 direct/cache/HTTPS checks pass while Mac1 direct ports time out and normal HTTPS still returns200. A counters allow76/drop3; B allow74/drop4. Rollback clears only project rules/references, verifies unchanged main filters and preserves each host's original PF mode. Mac1 directA/B and HTTPS then return200. [Operator timeline](../evidence/verification/2026-11-23-isolation-operator-evidence.json), [allowed edge](../evidence/verification/C-edge-allowed-20261123T062327Z.txt), [denied client](../evidence/verification/C-client-denied-20261123T062338Z.txt), [restored client](../evidence/verification/C-client-restored-20261123T063514Z.txt) |
| D — Backend HA | ReadyA6/B6; confirmed A unavailable; twelve B-only200 responses; A restarted under manager; recoveredA6/B6. [Timeline](../evidence/verification/2026-11-23-ha-repair-and-recovery.json), [outage](../evidence/verification/D-a-down-20261123T060400Z.txt), [recovery](../evidence/verification/D-recovered-20261123T060959Z.txt) |
| TLS approval / trust | Team confirms faculty approval of mkcert. Original primary certificate and normal HTTPS trusted on all four clients. [Approval](../evidence/verification/2026-11-23-faculty-mkcert-confirmation.txt), [Mac3](../evidence/verification/TLS-mac3-client-20261123T061208Z.txt), [Mac4](../evidence/verification/TLS-mac4-client-20261123T061225Z.txt) |
| E — Standby preflight | Separate same-CA leaf installed on Mac3; trusted explicit-route checks pass on all four clients, with standbyA6/B6 and conditional304. These preflights do not establish authoritative DNS migration. Cached-old/fresh-new cutover, convergence and restoration remain pending. [Operator preflights](../evidence/verification/2026-11-23-standby-client-preflights.json), [Mac2 cache](../evidence/verification/E-standby-https-20261123T070252Z.txt), [Mac2 balance](../evidence/verification/E-standby-balanced-20261123T070254Z.txt) |
| Saved capture / packet index | Pending actual binary pcap/pcapng and its derived frame index. Backup tcpdump text and historical screenshots do not replace that file. [Acquisition guide](../docs/packet-evidence.md) |
| Remaining failure rehearsal | Effective wrong-client-DNS configuration and remaining required failure/restore observations remain pending. Historical explicit dig to a public resolver is not an effective-client-setting demonstration. |

## Repairs and evidence limits

Earlier failures remain in the ledger and evidence directory. They include stale
manual backup-DNS data, old backend processes serving incompatible ETags, a colliding
untracked evidence file that blocked checkout updates, and a later stopped B process.
The corrected role-checked checkout updater preserves original colliding logs before
fast-forwarding. Runtime/cache checks reject the old application instead of relying
only on a200 status. The background manager starts only the intended application.
Subsequent controlled successful runs in the table supersede those failed baselines.

The first TTL restore-labelled check predates its scheduled change, so it is retained
as a pre-change baseline. Later genuine post-change restores and checks establish
cleanup. An initial manual-flush cleanup check failed and is also retained; the later
passing check supplies acceptance. All timing claims derive from actual outputs.

Keep host lids open and use a temporary caffeinate assertion for the lab. A primary
DNS non-answer coincided with an availability issue; current diagnostics and later
success do not establish its definitive cause. The managed ICMP limitation must be
disclosed. No broad firewall disable or invented successful ping is used.

## Six extension learning summaries

**A — Backup DNS.** A second DNS process makes the name service resilient only if
client settings actually include it and both servers agree on project records.
A cached successful lookup is not proof of backup use. Our test procedure ties a
stopped primary/listener absence, fresh system lookup, normal HTTPS and a query
received by the backup to one timeline, then restores primary DNS. An application
outage differs because the name can resolve even when no healthy app is available.

**B — TTL.** TTL is cache freshness, not an automatic broadcast that forces all
clients to change destinations. A genuine temporary client caching resolver makes
remaining TTL visible while forwarding to the real project DNS pair. Separate
natural-expiry and before-expiry manual-flush experiments distinguish the two
behaviors. Scheduled changes on both resolvers avoid confusing inconsistent DNS
with caching. This models controlled service migration and cutover delays.

**C — Isolation.** Backend ports are filtered at their hosts so ordinary clients
cannot bypass the TLS edge. A positive edge request, denied client request and
rule counters must be observed together; a timeout alone could also mean a stopped
backend. The corrected procedure verifies the parent anchor and records before
state and its own PF enable token. Clearing only owned rules and releasing that
token restores the prior policy without disabling another system component's PF.

**D — Backend HA.** Passive nginx detection learns failure from requests, retries
eligible GET traffic to another upstream and suppresses failed peers temporarily.
With A unavailable, B must serve every measured request successfully; after A returns,
both identities must reappear. Shared upstream state coordinates workers. This
protects against backend failure, while the primary edge remains a SPOF until a
second edge and an appropriate automatic VIP/DNS mechanism are available.

**E — Edge migration.** A valid standby presents the same hostname identity under
a trusted CA and proxies to the same backends; its leaf certificate need not be byte
identical. Synchronized DNS changes direct fresh lookups to standby while old-cache
clients may still use primary. The experiment measures this window, convergence
and both-server restoration. C is rolled back before the required E demo; the
optional combined policy temporarily admits both designated edges while denying
ordinary clients. This is controlled manual cutover, not automatic edge failover.

**F — Diagnosis.** We check DNS answers and the effective system lookup, then TCP,
TLS and edge/app layers, performing direct backend tests from the permitted edge.
Wrong DNS, wrong destination port, trust failure and upstream502 have different
causes. Each hypothesis needs supporting evidence and an appropriate recovery
check. Rehearsal can be recorded beforehand, but the faculty's actual fault, layer,
reasoning, fix/isolation and outcome are written only after the challenge occurs.

## Demonstration and completion

Use the [11-step final runbook](../docs/phase2-demo-runbook.md). Before submission,
finish the pending rows and run the strict artifact gate. Local regression checks
are described in [local validation](local-validation.txt); isolated loopback tests
prove implementation behavior, not four-Mac LAN acceptance. Keep the saved binary
capture with its actual frame/stream index and use it in the demonstration.

Each member explains the complete flow and extensions personally. Record the actual
faculty challenge's fault, hypothesis, layer, fix/isolation and result after it occurs.
The individual viva remains a live assessment.
