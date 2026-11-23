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
