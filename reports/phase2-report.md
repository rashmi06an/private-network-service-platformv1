# Phase 2 report — Harden, Recover and Troubleshoot

Team Scout Regiment. Current implementation and operating procedures updated on
22 November 2026. **Live acceptance remains open** until the actual outputs in
[verification-status.json](verification-status.json) are reviewed. This report
does not certify pending experiments or the not-yet-administered faculty challenge.

## System and changes since Phase 1

| Machine | Role | Current service address |
|---|---|---|
| Mac 1 Rashmi | primary DNS + client |10.7.27.145:53|
| Mac 2 Samiksha | primary edge/TLS/LB |10.7.25.25:8443|
| Mac 3 Shubhaang | Backend A + standby |10.7.28.78:3001 and :8443|
| Mac 4 Ankit | Backend B + backup DNS |10.7.27.247:3002 and :53|

Phase 1's same backend/DNS/edge roles are retained. Phase 2 adds a second resolver,
short TTL with synchronized record changes, narrow backend isolation, explicit
passive-backend retry/suppression and a second controlled edge. Historical Phase 1
already demonstrated default nginx retry around a stopped backend; Phase 2 makes
the policy and recovery measurement explicit, rather than claiming no prior failover.
See [inventory](../docs/network-inventory.md) for old/current addresses and
[architecture](../docs/architecture.md) for layer-by-layer flows.

The corrected source also supplies stable cross-backend cache representation/ETag,
X-Edge on every endpoint, assertions with meaningful exit status, scoped-DNS setup,
owned-anchor rollback, per-member commands and a truthful evidence ledger.

## Results and traceability

Existing screenshots are historical and indexed by [actual content](../evidence/phase2/INDEX.md).
They support several successful components, but do not establish all required
current experiments. Some images show DNS divergence and unsuccessful cache flush;
these are retained as diagnostic findings. The ledger is the authoritative place
for reviewed new artifact paths/results. Mandatory pre-review proof remains pending
until populated; the full source fix alone is not a completed network experiment.

Actual baseline received22 November: Mac 2 IP10.7.25.25; after starting nginx,
trusted by-name HTTPS returned200 fromB. Direct A:3001 failed; direct B:3002 returned200.
Primary DNS answered.25.25, backup answered.28.78. Mac 4 process inspection established
that its backup was running a different manual config file with app/api pointing
at standby and no TTL answer. These observations explain the repair order; they
are not represented as final acceptance. Updated/repaired results will be linked
as the team provides them.

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

## Final demonstration and report completion

Follow all 11 [demonstration steps](../docs/phase2-demo-runbook.md). Every member
participates and explains the complete system personally. After reviewing actual
new outputs, fill artifact paths/results in the ledger and add a concise factual
test-result table here. Keep the live challenge and individual viva correctly
identified until performed. Do not replace missing results with expected outputs.

## 23 November repair observation

Ankit supplied [backup restart/query output](../evidence/verification/2026-11-23-mac4-backup-dns-restored.txt): new manual dnsmasq process 87561, app and ttl names returning 10.7.25.25 with TTL 30 from localhost and its own LAN address. This corrects the prior stale-answer observation for those queries. Cross-Mac reachability, API parity and a fresh system lookup during a controlled primary outage remain pending. The acceptance ledger stays open.
