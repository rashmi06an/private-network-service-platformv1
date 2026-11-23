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

### Cross-Mac follow-up

[Mac 2 comparison and HTTPS](../evidence/verification/2026-11-23-mac2-dns-https-baseline.txt) now establishes backup reachability over the LAN, matching app/api answers, and a normal HTTPS 200 response from A after system-cache flush. The TTL record still differs between primary and backup. X-Edge is absent, and shared cache validation/new-config deployment remain unverified. This is partial baseline progress, not a completed failover/TTL experiment.

### Primary canonical configuration applied

At 03:50:00–03:50:09 UTC on 23 November, Rashmi ran the canonical primary setup at commit cec41e5. The [recorded setup output](../evidence/verification/R1-primary-setup-20261123T035000Z.txt), copied from the team-supplied transcript with formatting normalized, shows saved pre-change configuration, syntax validation, service restart, all three records at 10.7.25.25 TTL30, and exit0. This supersedes the earlier primary-local TTL mismatch observation. Backup canonical migration and the complete fresh-client failover experiment remain pending.

### Backup canonical configuration applied

Ankit supplied the [backup setup log](../evidence/verification/R1-backup-setup-20261123T041652Z.txt) for 04:16:52–04:16:56 UTC on 23 November, commit16ff0bd. It is copied from the team transcript with formatting normalized. The canonical backup setup saved prior config, passed syntax validation, restarted the managed service and checked app/api/ttl at 10.7.25.25 TTL30, with exit0. Both canonical DNS setup stages are now observed successful; the full cross-client primary-outage/fresh-lookup experiment is still pending.

### Current edge baseline: mixed backend deployment detected

The [Mac2 Round1 transcript](../evidence/verification/2026-11-23-mac2-round1-transcript.txt)
is copied verbatim from the user-supplied terminal text, including older scrollback.
The five new recorder files retain their exact START/END blocks from that transcript.
At04:48 UTC, the current results are:

| Check | Observed result |
|---|---|
| Scoped client DNS on Mac2 | Both private DNS servers installed and effective; a second client's settings remain pending |
| Canonical primary edge | Config validation and apply succeeded; trusted responses carry X-Edge primary-mac2 |
| Both DNS datasets from Mac2 | All six app/api/ttl answers match10.7.25.25 with TTL30; the earlier scrollback TTL mismatch is superseded |
| Direct backend health | Both200/identity checks passed the old helper, but A lacked no-store and was serving the old runtime |
| HTTPS cache validation | Failed: B returned team1-cache-v2, then A returned backend-a-v1 with200 instead of the required304 |
| HTTP/2 | Actual trusted HTTP/2 responses observed; the separate HTTP2 command was skipped after the cache failure |
| Load-balancing command | Not executed because the preceding HTTPS check failed in the && chain |

The earlier local updated-A response is retained as historical evidence, but current
runtime acceptance remains open. The direct checker now requires no-store, the shared
v2 ETag, cache policy and conditional304 independently from both backends. Its
regression fixtures reject old A, old B, an old validator with otherwise new status,
and a broken conditional response, while accepting both updated backends. Identify
the active Mac3 process and relaunch the corrected A before repeating the baseline.

### Baseline restored and verified at04:55 UTC

Shubhaang supplied a successful corrected-A startup at04:55:26 UTC from
`Documents/CN-submission`, commitdedf0d9. The subsequent Mac2 rechecks supersede
the mixed-deployment failure above. The following original recorder files were
copied byte-for-byte from Mac2's CN-submission checkout, rather than reconstructed
from expected output:

| Actual check | Observed result |
|---|---|
| [Both updated backends](../evidence/verification/R1-backends-recheck-20261123T045542Z.txt) | Both200 with correct identity, no-store, shared team1-cache-v2 and direct304; exit0 |
| [Trusted hostname HTTPS/cache](../evidence/verification/R1-https-cache-recheck-20261123T045543Z.txt) | HTTP2 status200, cache200 fromA followed by304 fromB with the shared ETag and primary-mac2; exit0 |
| [Load balancing](../evidence/verification/R1-balanced-recheck-20261123T045544Z.txt) | Twelve200 responses, A6/B6; exit0 |
| [Explicit HTTP2](../evidence/verification/R1-http2-recheck-20261123T045545Z.txt) | HTTP_CODE_AND_VERSION=200 2; exit0 |

Baseline and cache/HTTP2 ledger items are now verified. Controlled DNS failover,
a second client's resolver settings, TTL experiments, isolation/rollback, backend
HA, standby cutover, saved capture/index, remaining inventory/rehearsal and CA
approval evidence are still separate pending items. Live faculty challenge and
individual viva remain live evaluation tasks.

### Client settings verified; inventory corrections still open

Mac3's [dual-DNS installation](../evidence/verification/R2-mac3-client-dns-20261123T050122Z.txt)
at05:01:22-05:01:26 UTC passes, verifying the two-client setting requirement with
Mac2. [Three further inventories](../evidence/verification/2026-11-23-three-mac-inventory-observations.json)
confirm the remaining assigned addresses and hardware/network fields. Nine of the
twelve directed ping results pass; three fail toward Mac1, whose recorded stealth
mode is ON. The change/retest outcome is not yet supplied. Mac4 also still uses
the old private resolver10.7.17.21, while Mac1 uses localhost only; canonical client
DNS installation on both remains pending. Controlled primary-outage evidence is
still a separate required experiment.

### Managed policy prevents the ICMP correction

At05:05:58 UTC the Mac1 stealth setter reported that managed Macs cannot modify
this setting from the command line, despite exit0. Its readback still says ON.
The [recorded observations](../evidence/verification/2026-11-23-managed-stealth-and-dns-rechecks.json)
retain this unresolved acceptance gap; a permitted IT/faculty change or explicit
assessment exception is needed. Current private-zone DNS installs now pass on all
four Macs. Mac4's separate Wi-Fi DNS list retains the old primary address and needs
cleanup with original-list backup/readback. DNS failover remains unverified until
a controlled outage, fresh system lookup/HTTPS, backup receipt and restoration are
captured; script timestamps now distinguish direct-dig checks from normal lookup.
