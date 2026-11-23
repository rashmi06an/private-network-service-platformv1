# Evidence collection commands

The authoritative current per-member commands are [team-commands.md](team-commands.md).
Do one round at a time. Use `scripts/record-evidence.sh LABEL command...` to save
unmodified output, UTC start/end, host, repository commit, command and exit status.

Screenshots should include the command, output, host/role and relevant timestamps.
Do not label a file PASS if it only shows expected text or a failed attempt.
Save saved captures as pcapng too, with a packet index. See
[packet-evidence.md](packet-evidence.md) and [ttl-experiments.md](ttl-experiments.md).

- A: both resolvers/all three records identical, effective client settings,
  primary stopped/no listener, backup query receipt, fresh by-name HTTPS, restore.
- B: one timed natural-expiry run and a separate before-expiry manual-flush run.
- C: exact rules and counters on both backend Macs, edge allowed, client denied,
  by-name HTTPS while active, owned-anchor/token rollback and restored direct access.
- D: balanced → A listener stopped → B-only 200 → A listener restarted → A/B 200.
- E: standby config/HTTPS, both DNS answers updated, cached-old/fresh-new clients,
  convergence, both DNS answers restored and primary HTTPS healthy.
- F: rehearsal result now; the actual faculty fault/result only after it happens.

Historical image filenames are indexed by their actual contents, not taken as
claims of current success. Do not overwrite historical evidence with new output.
