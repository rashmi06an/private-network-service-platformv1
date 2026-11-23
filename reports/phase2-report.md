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

### Extension A verified: controlled primary outage and restoration

| UTC on23November | Actual evidence |
|---|---|
| 05:15:26–05:15:34 | [Rashmi stopped primary DNS](../evidence/verification/A-primary-stop-20261123T051526Z.txt); the accompanying port53 listing had no listener rows |
| 05:15:45–05:15:53 | [Mac2 after cache flush](../evidence/verification/A-primary-down-20261123T051545Z.txt): primary non-answer, backup's three correct answers, system lookup10.7.25.25 and normal trusted HTTP2/200 with primary-mac2 |
| 05:15:51.712912–05:15:51.716443 | [Ankit's actual backup receipt](../evidence/verification/A-backup-receipt-20261123T051432Z.txt): normal resolver A query ID38321 fromMac2 UDP50756 to backup53, followed by10.7.25.25 answer |
| 05:16:40–05:16:41 | [Primary restored](../evidence/verification/A-primary-restore-20261123T051640Z.txt) |
| 05:16:53–05:16:54 | [Both datasets checked fromMac4](../evidence/verification/A-restored-20261123T051653Z.txt), all six names/IP/TTL checks pass |

The backup receipt also contains the three earlier explicit-dig requests at05:15:48;
those are separated from the later normal resolver A transaction above. The native
Mac2 recorder file was copied directly; other files are faithful transcriptions of
actual team-pasted output. The supplied receipt excerpt has no completed capture
exit-code footer, so no such code is invented. This text receipt proves Extension A
but does not replace the separate mandatory saved binary packet capture/frame index.
The DNS-failover ledger item is now verified. [Fresh Mac4 service readback](../evidence/verification/2026-11-23-mac4-wifi-dns-final-readback.txt)
at05:18:49 UTC is only8.8.8.8, confirming stale service DNS cleanup.

### Extension B natural expiry verified and restored

The [original live Mac2 recorder](../evidence/verification/B-expiry-20261123T052539Z.txt)
shows priming at05:29:01.066 UTC with30seconds and OLD10.7.25.25. Both real DNS
servers returned NEW10.7.28.78 at05:29:06 while the real client cache still returned
OLD/TTL25. Its remaining TTL declined25,23,...,1; NEW/TTL30 appeared at05:29:32.553,
31.49seconds after priming, without a manual flush. The client exited0.

[Timeline/provenance](../evidence/verification/2026-11-23-ttl-expiry-timeline.json)
retains the early user restores at05:26 and the05:27 both-up file, but these predate
the scheduled05:29:04 change and do not prove final restoration. After completion,
Ankit supplied a new restore at05:30:48 and Rashmi at05:31:07. The agent then ran
[the actual final Mac2 both-up check](../evidence/verification/B-expiry-final-restored-20261123T053310Z.txt)
at05:33:10–05:33:11, obtaining all six normal records/TTL30 and exit0. Natural expiry
and its restoration are verified; the distinct manual-flush case remains pending.

### Separate manual-flush client case passed; cleanup under review

The agent ran [the live Mac2 manual-flush helper](../evidence/verification/B-manual-flush-20261123T053519Z.txt)
against the two operators' shared epoch1795412219. At05:37:01 UTC both authorities
served NEW while the client retained OLD/TTL25. The explicit SIGHUP to its owned
cache PID85419 immediately obtained NEW at05:37:01.311, only5.25seconds after
priming, with exit0. This is separate from the31.49-second natural-expiry run.
The [first cleanup check](../evidence/verification/B-flush-final-restored-20261123T053836Z.txt)
at05:38:36 still found primary ttl pointing to NEW, so the full manual-flush ledger
item remains pending until post-experiment restores and a passing final check.

### Manual-flush restoration verified; B availability gap found separately

User supplied primary restore05:38:49 UTC and backup restore05:40:37. The
[final Mac2 check](../evidence/verification/B-flush-restored-recheck-20261123T054126Z.txt)
at05:41:26 passes all six normal answers/TTL30, completing manual-flush acceptance.

A separate [HA baseline](../evidence/verification/D-balanced-20261123T054032Z.txt)
at05:40:32–05:40:39 found12 successful A responses and no B. The
[direct diagnosis](../evidence/verification/D-backend-diagnosis-20261123T054128Z.txt)
confirmed current A v2/304 and failed B3002 connectivity; Ankit then supplied an
unchanged10.7.27.247 address and empty port3002 listener listing. Baseline is reopened
until B is restored. A new role-checked backend manager starts the fixed checkout
in a detached session, checks current application behavior, logs locally, and checks
UID/PID/birth/app path before stopping its own process. It refuses other listeners.
Real isolated-process tests cover start/status/idempotence/stop/restart, wrong Mac,
occupied port and unrelated PID refusal. Live B deployment and required controlled
A-down/B-only/recovery evidence remain pending.

The cache routes also omit the application-generated Date after conditional
processing, allowing the serving layer to emit one wire Date. Native loopback
checks of both apps'200 and304 responses now assert exactly one Date header.
The complete regression suite currently passes nine test methods, including
background process lifecycle/refusal and effective wrong-DNS rollback fixtures.

### Extension D verified: ready baseline, A outage and recovery

[Full timeline/provenance](../evidence/verification/2026-11-23-ha-repair-and-recovery.json)
retains the earlier B outage and subsequent DNS non-answer rather than representing
those failed checks as passes. B was restored under the background manager with
PID82111. Mac1 later reported healthy local DNS and began a temporary keep-awake
assertion; all six live DNS records and committed trusted HTTPS checks passed again.
No definitive cause of the earlier intermittent primary non-answer is asserted.

| Controlled stage | Actual result |
|---|---|
| [Ready baseline](../evidence/verification/D-balanced-ready-20261123T055933Z.txt) | 05:59:33-38 UTC: A6/B6, twelveHTTP200 |
| [A unavailable](../evidence/verification/D-a-unavailable-20261123T060359Z.txt) | Guarded user stop of PID22992; Mac2 direct3001 connection refused |
| [A-down](../evidence/verification/D-a-down-20261123T060400Z.txt) | 06:04:00-07 UTC: A0/B12, allHTTP200 |
| [Restart A](../evidence/verification/D-a-restart-20261123T060845Z.txt) | 06:08:45 UTC: fixed checkout background PID24638, exit0 |
| [Recovered](../evidence/verification/D-recovered-20261123T060959Z.txt) | 06:09:59-06:10:04 UTC: A6/B6, allHTTP200 |
| [Current apps](../evidence/verification/D-recovered-apps-20261123T061004Z.txt) | Both no-store, shared-v2 ETag, direct304 and single wireDate |
| [Trusted edge](../evidence/verification/D-recovered-https-20261123T061004Z.txt) | Normal hostname HTTP2/200 and304, primary-mac2 |

The edge remains a single point of failure until the separate standby exercise;
this controlled backend recovery is not automatic edge failover. Baseline and HA
ledger items are verified again. The team also [confirmed faculty mkcert permission](../evidence/verification/2026-11-23-faculty-mkcert-confirmation.txt);
public certificate identity is valid, while the remaining clients' trust checks
are still required separately.

### All-client trust verified and isolation baseline captured

The team confirmed faculty permission for the existing mkcert method. Mac2 already
has multiple trusted200/304 proofs. [Mac1's pre-isolation check](../evidence/verification/C-before-isolation-20261123T061158Z.txt)
confirms both direct backend ports currently return200 and normal hostname HTTPS
works without a trust bypass. [Mac3](../evidence/verification/TLS-mac3-client-20261123T061208Z.txt)
and [Mac4](../evidence/verification/TLS-mac4-client-20261123T061225Z.txt) each then
passed trusted hostname200/304. These are faithful transcriptions of team-pasted
recorder blocks, with formatting normalized. Certificate-method approval and all
four client trust checks are now verified. Firewall apply/denial/counters/rollback
still need their actual controlled trial. The apply helper now records pre-PF info
and requires a filter-anchor call, rather than accidentally matching a scrub anchor.
