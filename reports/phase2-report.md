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

## Reviewed results - all pre-evaluation items verified

| Requirement | Actual result | Evidence |
|---|---|---|
| LAN/inventory | All four inventories;12 directed successful paths across baseline/follow-up. | [Open](../docs/network-inventory.md) |
| Baseline/cache/HTTP2 | Both v2 apps, A/B balancing, trusted HTTPS200/304 and actualHTTP2. | [Open](../evidence/verification/D-recovered-https-20261123T061004Z.txt) |
| Client DNS | Both current resolvers effective on all four clients. | [Open](../evidence/verification/R2-mac4-client-dns-20261123T050617Z.txt) |
| A - Backup DNS | Primary stopped; fresh system lookup/HTTPS via backup; query receipt; restore. | [Open](../evidence/verification/A-primary-down-20261123T051545Z.txt) |
| B - Natural expiry | Real OLD retained until31.49s, then NEW; both authorities restored. | [Open](../evidence/verification/B-expiry-20261123T052539Z.txt) |
| B - Manual flush | Separate explicit flush obtains NEW at5.25s, before30s expiry; restore. | [Open](../evidence/verification/B-manual-flush-20261123T053519Z.txt) |
| C - Isolation | Edge allowed/client denied; counters; scoped rollback and both direct accesses restored. | [Open](../evidence/verification/2026-11-23-isolation-operator-evidence.json) |
| D - Backend HA | A6/B6 baseline; A down gives12B/200; restart givesA6/B6 again. | [Open](../evidence/verification/2026-11-23-ha-repair-and-recovery.json) |
| E - Edge cutover | Concurrent cached-old primary/fresh-new standby; natural31.44s convergence; both-DNS/primary restore. | [Open](../evidence/verification/E3-cutover-review.json) |
| Saved packet flow | Original57packets: DNS1/3; TCP6/7/8; TLS Certificate13/38; CCS; encrypted data; h2. | [Open](../evidence/verification/packet-index.md) |
| Failure rehearsal | Effective wrong-client DNS failure/IP control and restored HTTPS200/304; other historical outcomes indexed. | [Open](../evidence/verification/2026-11-23-mac3-wrong-client-dns-reviewed.json) |
| TLS method/trust | Faculty mkcert permission confirmed by team; all four clients trust primary and standby leaf. | [Open](../evidence/verification/2026-11-23-standby-client-preflights.json) |

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

## Final restoration and provenance

After the timed cutover, Mac1 app record was restored07:55:59 UTC and Mac4 at07:56:42.
[Final DNS](../evidence/verification/E3-final-dns-20261123T075709Z.txt) returns all6
normal app/api/ttl answers with TTL30. [Final trusted HTTPS](../evidence/verification/E3-final-https-20261123T075710Z.txt)
returns primary200/304 and both backend identities. Native connected-IP observation
is10.7.25.25. Mac2's original dual-DNS scoped file is restored and temporary cache
removed. Standby remains available for demonstration; normal DNS points to primary.

Native Mac2 logs and AirDropped pcap bytes are originals. Other operators' supplied
recorder blocks/observations are faithfully transcribed and labelled. Historical
screenshots are unchanged from main. Earlier failed attempts remain as diagnostic
history; the latest successful results supersede them. No packet numbers or missing
operator timestamps are fabricated. The [13-item ledger](verification-status.json)
and [final validation](final-validation.json) distinguish local fixtures from LAN trials.

## Demonstration

Use the [11-step runbook](../docs/phase2-demo-runbook.md) and saved packet capture.
The faculty's actual injected fault and each member's viva remain live assessment
requirements; completed rehearsal does not claim they have already occurred.
