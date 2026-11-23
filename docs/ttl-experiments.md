# TTL experiments with a real client cache

Direct `dig @primary` reads freshly generated authoritative/local-record answers,
so those answers keep their configured TTL of 30. It does not show a client cache
counting down. We use an actual temporary dnsmasq cache on **Mac 2**, bound only to
127.0.0.1:53535, forwarding to the two real team DNS servers. No synthetic DNS
answers or fake cache are used. It needs `brew install dnsmasq` on Mac 2 once.

The 30-second window is short. Schedule record changes on both DNS Macs using
one shared future Unix epoch. Their clocks must agree; compare `date -u` first.
If either server misses the schedule or has the wrong records, stop, restore both
and repeat; a half-completed run is diagnostic evidence, not a pass.

## Before each test

1. Confirm baseline on Mac 2: `scripts/test-backup-dns.sh both-up`.
2. For expiry/flush, BOTH Mac 1 and Mac 4 restore:
   `scripts/dns-record.sh ttl 10.7.25.25`.
3. For cutover, BOTH restore `scripts/dns-record.sh app 10.7.25.25`, keep the
   standby running, and confirm both backends reachable by that standby.
4. Mac 2 chooses an epoch about three minutes ahead:

```bash
python3 -c 'import time; print(int(time.time()) + 180)'
```

Share the printed number. In the commands below replace `EPOCH` with that same
number on all three Macs. It is a schedule value, not text to type literally.

## Natural expiry — no manual flush during the cache lifetime

**ARMED means waiting, not finished.** Start the two scheduled DNS commands and
then the client experiment. Keep all three terminals open. Do not run the restore
or final both-up check until the client prints PASS or FAIL and finishes. Any
both-up output timestamped before the scheduled epoch is only a pre-change baseline,
even if its evidence label contains the word restored. After completion, restore
both DNS servers and obtain a new both-up result after their changes/rollback.

**Mac 1 and Mac 4**, each in its own terminal:

```bash
scripts/record-evidence.sh B-expiry-record scripts/dns-record.sh ttl 10.7.28.78 EPOCH
```

**Mac 2**, started at least 12 seconds before the epoch:

```bash
scripts/record-evidence.sh B-expiry python3 scripts/ttl-experiment.py expiry EPOCH
```

The real cache is primed just before change. Both servers must show NEW while
the cache still shows OLD. Queries print timestamps and declining remaining TTL;
the script asserts that the client eventually receives NEW after natural expiry.
It terminates only its own temporary resolver when finished.

Then BOTH DNS Macs restore `scripts/dns-record.sh ttl 10.7.25.25` and Mac 2
verifies `scripts/test-backup-dns.sh both-up`.

## Manual flush — separate experiment, before natural expiry

Choose a NEW future epoch and schedule the same ttl-record update on both Macs.
On Mac 2 use:

```bash
scripts/record-evidence.sh B-manual-flush python3 scripts/ttl-experiment.py flush EPOCH
```

It proves authoritative NEW plus cached OLD, sends SIGHUP only to the owned
temporary cache process, then requires immediate NEW before 30 seconds pass.
This is a manual DNS-cache flush; `dscacheutil` alone cannot expose its TTL.
Restore ttl on BOTH DNS Macs and verify the normal answers again.

## Edge migration — real by-name HTTPS and cached-old behavior

This requires the corrected primary/standby configs, trusted certificate on the
standby, normal source services up, and C firewall rollback (or the explicit
two-edge policy). Use a NEW shared future epoch:

**Mac 1 AND Mac 4:**

```bash
scripts/record-evidence.sh E-record scripts/dns-record.sh app 10.7.28.78 EPOCH
```

**Mac 2:**

```bash
scripts/record-evidence.sh E-cache-cutover python3 scripts/ttl-experiment.py cutover EPOCH
```

For this mode only, the helper backs up Mac 2's scoped resolver file and points
it at the real local caching resolver on 10.7.25.25:53. It performs normal hostname HTTPS requests
with no `--resolve` and no `-k`: before change → primary; after servers change but
while cached → primary; after natural expiry → standby. It checks connected IP,
HTTP 200 and X-Edge. The original scoped file is restored even after a failed test.

**Mac1:** chain this after its successful scheduled app-record update in the same
terminal, so it starts automatically when that update completes:

```bash
scripts/record-evidence.sh E-fresh-mac1 scripts/fresh-cutover-client.sh EPOCH
```

The role-checked helper waits until epoch+5seconds, flushes the actual system DNS
cache, obtains a normal system lookup, then performs trusted hostname HTTPS with
no --resolve/-k. It requires the standby connected IP/X-Edge and completion before
epoch+25seconds. Late/mismatched results fail rather than being labelled coexistence
proof. Prepare both DNS schedules and the Mac2 client before the shared epoch.

This fresh client should reach standby while Mac 2 still holds its old cached
answer. Record both timestamps. After every cutover, BOTH DNS Macs restore:

```bash
scripts/dns-record.sh app 10.7.25.25
```

Mac 2 runs `scripts/test-backup-dns.sh both-up` and `scripts/test-https.sh`.
Mac 3 stops only its standby nginx with `sudo nginx -s quit` after migration is
fully restored; do not stop Backend A. Preserve the actual experiment output,
including failures, and review it before accepting a pass.

### Current macOS compatibility

Expiry/flush query the temporary localhost cache directly on port 53535. Cutover
uses a project-owned temporary DNS daemon on the actual Mac 2 LAN IP, port 53,
with sudo and an exact PID file. This avoids current macOS ignoring localhost
scoped overrides on a non-53 port. The helper refuses existing listeners, restores
the original scoped DNS file and terminates only its own DNS daemon afterwards.

### Local helper validation before the team run

[Isolated native-dnsmasq validation](../reports/ttl-cache-local-validation.json)
ran the expiry/flush helper against two owned loopback high-port dnsmasq authorities,
with explicit source-copy substitutions for their addresses/ports and temporary
state root. It observed natural refresh at31.19seconds and a separate manual flush
at5.27seconds. This tests the helper's actual DNS-cache behavior; it is not evidence
that the four-Mac experiment ran. The live expiry/flush ledger items remain pending.
Use different evidence labels for the two DNS operators (for example,
B-expiry-record-mac1 and B-expiry-record-mac4) so their files remain distinct.

For cutover only, the client also clears its own temporary resolver immediately
before priming the measured TTL interval, preventing an unrelated background lookup
while armed from shortening it. This is preparation before the measured cache
lifetime, not a manual flush during the natural-expiry window. Daemon ownership
checks use full ps arguments so long checkout paths do not hide the config identity.
