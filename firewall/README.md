# Backend isolation with project-owned PF rollback

Mac 3 :3001 and Mac 4 :3002 deny ordinary LAN clients. During Extension C, only
the primary edge Mac 2 (10.7.25.25) is permitted. Rules are scoped to en0/IPv4,
the actual backend destination and its one service port.

On BOTH backend Macs:

```bash
scripts/record-evidence.sh C-apply scripts/firewall-isolation.sh apply primary
scripts/firewall-isolation.sh show
```

The helper verifies the reachable parent `anchor "com.apple/*"`, then loads only
`com.apple/team1_submission`. It saves the main rules/config before changing,
owns a separate PF enable reference and records the returned token locally.
Loading a detached arbitrary anchor would not be sufficient.

**Mac 2:** `scripts/record-evidence.sh C-edge-allowed scripts/test-backends.sh`.
**Mac 1:** `scripts/record-evidence.sh C-denied scripts/test-backend-isolation.sh isolated`.
Save the rule counters from both backend Macs at the same time.

Rollback on BOTH backends:

```bash
scripts/record-evidence.sh C-rollback scripts/firewall-isolation.sh rollback
```

Then Mac 1 runs `scripts/test-backend-isolation.sh restored`. Only project anchor
rules are cleared and the project's enable token released. Other rules/owners
are left in place; a global `pfctl -d`, global flush, or generic `/etc/pf.conf`
reload is not the rollback recipe.

## Interaction with standby migration

The required C demonstration ends with rollback, then E can be demonstrated on
the original LAN policy. The normal C-only policy deliberately does not allow
Mac 3 to access Backend B. For an additional combined hardened cutover, both
designated edges need temporary access during cached-old/new coexistence:

```bash
scripts/firewall-isolation.sh apply both      # both backend Macs, if no project rules active
# OR, if project rules are already active:
scripts/firewall-isolation.sh set-edges both
```

Ordinary Mac 1 remains blocked. After DNS restoration switch back using
`set-edges primary`, or perform the required project rollback. This temporary
two-edge policy is explicitly distinguished from the strict Mac 2-only C proof.
