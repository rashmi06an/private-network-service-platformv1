# Coordinated member commands

Use the given addresses: Mac 1 10.7.27.145, Mac 2 10.7.25.25,
Mac 3 10.7.28.78, Mac 4 10.7.27.247. These are current assignments,
not permanent DHCP reservations. Stop if a preflight finds another IP.

Run one round, share its actual output, and check the results before moving on.
All commands below start from the new checkout root. Do not paste the whole
document into a terminal; the steps deliberately change/fail/restore services.

## Round 0 — each member obtains the corrected source

On each Mac, create this separate checkout once; it preserves the old submission:

```bash
git clone --branch samiksha/submission-readiness https://github.com/rashmi06an/private-network-service-platformv1.git "$HOME/Documents/CN-submission"
cd "$HOME/Documents/CN-submission"
git status --short
git rev-parse --short HEAD
```

For subsequent updates in this same branch: `git pull --ff-only`.
Do not run that over uncommitted evidence without saving it first.
Record each Mac's inventory and all three outbound pings:

| Member | Command |
|---|---|
| Rashmi | `scripts/record-evidence.sh R0-mac1 scripts/preflight.sh mac1` |
| Samiksha | `scripts/record-evidence.sh R0-mac2 scripts/preflight.sh mac2` |
| Shubhaang | `scripts/record-evidence.sh R0-mac3 scripts/preflight.sh mac3` |
| Ankit | `scripts/record-evidence.sh R0-mac4 scripts/preflight.sh mac4` |

## Round 1 — normal services (all backends and DNS up)

**Shubhaang / Mac 3:** stop the old Backend A in its original terminal using Ctrl+C.
In a new terminal, keep this updated backend running:

```bash
cd "$HOME/Documents/CN-submission/backend-a"
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python app.py
```

**Ankit / Mac 4:** stop the old Backend B with Ctrl+C, then use the same block
with `backend-b`. Keep its backend terminal open.

**Rashmi / Mac 1:** install the primary DNS config:

```bash
cd "$HOME/Documents/CN-submission"
scripts/record-evidence.sh R1-primary-setup scripts/setup-dns.sh primary
```

**Ankit / Mac 4:** the old backup runs manually with
`-C /Users/ankitrajsingh/team1-phase2/backup-dnsmasq.conf`, not the Homebrew service.
After primary DNS is confirmed working, stop that identified instance with Ctrl+C
in its original DNS terminal. Verify `sudo lsof -nP -iUDP:53 -iTCP:53` is empty;
do not stop unrelated listeners. Then:

```bash
cd "$HOME/Documents/CN-submission"
scripts/record-evidence.sh R1-backup-setup scripts/setup-dns.sh backup
```

`setup-dns.sh` deliberately refuses any remaining unknown port-53 process. Its
normal records now come from `/opt/homebrew/etc/team1-project.hosts`. Editing
the former manual config after this migration will have no effect.

**Every Mac that acts as a client:** install the scoped private resolver file and
trust the **public** root CA certificate per [TLS notes](../edge/tls-setup-notes.md):

```bash
scripts/client-dns.sh install
```

**Samiksha / Mac 2:** reuse the existing valid hostname certificate if present.
The helper expects `app.team1.test.pem` and `app.team1.test-key.pem` in
`/opt/homebrew/etc/nginx/certs`. It does not overwrite either key/certificate.

```bash
scripts/record-evidence.sh R1-edge-apply scripts/apply-edge.sh primary
scripts/record-evidence.sh R1-dns-sync scripts/test-backup-dns.sh both-up
scripts/record-evidence.sh R1-backends scripts/test-backends.sh
scripts/record-evidence.sh R1-https-cache scripts/test-https.sh
scripts/record-evidence.sh R1-balanced scripts/test-load-balancing.sh
```

Share all results. Expected: all three DNS records on both servers point to
10.7.25.25; both backends 200; X-Edge primary-mac2; 304 through HTTPS.

## Round 2 — backup DNS failover (Extension A)

1. Mac 2 and Mac 3 save their scoped DNS settings with `preflight.sh`.
2. Mac 4 opens another terminal and captures actual project DNS queries:

```bash
sudo tcpdump -ni en0 -l 'port 53 and host 10.7.25.25'
```

3. Mac 1: `sudo brew services stop dnsmasq`, then
   `sudo lsof -nP -iUDP:53 -iTCP:53` (no primary listener).
4. Mac 2, **while primary remains stopped**:

```bash
sudo dscacheutil -flushcache
sudo killall -HUP mDNSResponder
scripts/record-evidence.sh A-primary-down scripts/test-backup-dns.sh primary-down
```

5. Save the Mac 4 query receipt with its time, and stop its tcpdump with Ctrl+C.
6. Mac 1 restores: `sudo brew services start dnsmasq`.
7. Mac 2: `scripts/record-evidence.sh A-restored scripts/test-backup-dns.sh both-up`.

Do not claim OS failover from a cached lookup or an explicit backup-only dig alone.

## Round 3 — TTL expiry and separate manual flush (Extension B)

Follow [ttl-experiments.md](ttl-experiments.md). Samiksha runs a temporary real
client-side caching resolver; both DNS operators schedule the same record change.
Complete and restore the expiry test before starting the manual-flush test.

## Round 4 — backend HA (Extension D)

Mac 2: `scripts/record-evidence.sh D-balanced scripts/test-ha-failover.sh balanced`.
Mac 3 stops **only Backend A** using Ctrl+C and records that :3001 has no listener.
Mac 2: `scripts/record-evidence.sh D-a-down scripts/test-ha-failover.sh a-down`.
Mac 3 restarts updated Backend A with the Round 1 launch block.
Wait 11 seconds for the failed upstream's suppression period, then Mac 2:
`scripts/record-evidence.sh D-recovered scripts/test-ha-failover.sh recovered`.

For the Phase 1 both-down case, stop B too, prove HTTPS returns 502 at the edge,
then restore both and rerun HTTPS/balancing. Do this only as its own controlled test.

## Round 5 — isolation and exact rollback (Extension C)

Keep both backends up. Mac 3 AND Mac 4:

```bash
scripts/record-evidence.sh C-rules scripts/firewall-isolation.sh apply primary
```

Mac 2: `scripts/record-evidence.sh C-edge-allowed scripts/test-backends.sh`.
Mac 1: `scripts/record-evidence.sh C-client-denied scripts/test-backend-isolation.sh isolated`.
Mac 3 AND Mac 4 save counters with `scripts/firewall-isolation.sh show`, then:

```bash
scripts/record-evidence.sh C-rollback scripts/firewall-isolation.sh rollback
```

Mac 1: `scripts/record-evidence.sh C-restored scripts/test-backend-isolation.sh restored`.
This clears only the project anchor and releases its own PF enable token. Do not
run a global `pfctl -d` or global rule flush. Keep `.local-state/pf-isolation` backups.

## Round 6 — standby edge and DNS cutover (Extension E)

Complete C rollback first, as the evaluation document requests after that demo.
For an optional combined hardened cutover, see [firewall README](../firewall/README.md)
for the explicit temporary two-edge policy; a Mac 2-only rule cannot admit Mac 3.

Mac 3 installs the valid hostname leaf certificate and leaf key (not CA signing key),
then: `scripts/record-evidence.sh E-standby-apply scripts/apply-edge.sh standby`.
Confirm direct standby connectivity without bypassing trust:

```bash
/usr/bin/curl --noproxy '*' --resolve app.team1.test:8443:10.7.28.78 -i https://app.team1.test:8443/api/status
```

This particular command isolates standby connectivity and is **not DNS-cutover proof**.
Use the `cutover` experiment in [ttl-experiments.md](ttl-experiments.md) for normal
hostname requests, cached-old vs new answers, convergence and restoration.
Save a fresh normal lookup/HTTPS result from Mac 1 during the TTL window too.

## Round 7 — saved packet capture, explanations and final rehearsal

Follow [packet evidence](packet-evidence.md) and the [11 steps](phase2-demo-runbook.md).
Every member prepares [viva notes](viva-notes.md). Review the actual new evidence,
update [the ledger](../reports/verification-status.json), then run:

```bash
python3 scripts/submission-check.py
```

The injected faculty challenge and personal viva are live tasks, not invented
pre-submission screenshots. Keep them explicitly identified in the final report.
