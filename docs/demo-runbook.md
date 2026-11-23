# Phase 1 historical checkpoint and current demonstration

Phase 1 was already submitted. Historical addresses and proofs remain in
[network inventory](network-inventory.md) and [phase1-report](../reports/phase1-report.md).
Some early DNS screenshots query 10.7.21.14; later same-phase evidence uses
10.7.17.21. The early screenshots are retained as earlier-session evidence, not
the current resolver address. All current commands use the Phase 2 addresses.

For the final evaluation use the corrected **[11-step runbook](phase2-demo-runbook.md)**.
Its caching endpoint is `/api/cache-demo`; `/api/status` intentionally has no
conditional validator. [Viva notes](viva-notes.md) now exist.

Required historical failure categories: wrong client resolver, wrong project DNS
record, one backend down, both down (502), wrong destination port. The existing
images support most outcomes. For the literal wrong-client-setting test, record
the effective bad private-zone resolver and failed normal lookup plus successful
IP ping, then restore the saved scoped file. An explicit @8.8.8.8 query alone is
only a diagnostic comparison, not a changed client configuration.

Do failure experiments as separate stages; restore baseline after each. Never use
old IPs from historical commands as the present service map.

### Effective wrong-client DNS rehearsal

`scripts/wrong-client-dns-demo.sh` first requires a passing trusted HTTPS/cache
baseline. It checks that the client's own LAN IP has no DNS port53 socket, then
uses that address on standard DNS port53 as the deliberately wrong scoped resolver.
It avoids current macOS ignoring localhost overrides on nonstandard ports. The
helper backs up the scoped file, flushes caches, proves IP reachability, requires
an actual curl resolution error, restores the prior file, and rechecks HTTPS/304.
A TLS/app failure is not accepted as a DNS-failure exhibit. Do not run it while a
cutover cache occupies the client's port53. Isolated OS-command fixtures cover
resolution failure/timeout and rollback, occupied-port refusal, unrelated TLS error,
and failed configuration installation. The actual live rehearsal remains pending.
