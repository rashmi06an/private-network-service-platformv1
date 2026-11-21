# Backend Service Isolation — Phase 2 / Extension C

Restrict direct access to the backend ports (3001, 3002) so that **only the
edge (Mac 2, `10.7.25.25`) can reach them**. Clients must go through the edge.

Uses the macOS packet filter, `pf`. The rulesets here are self-contained and
only touch the one backend port, so they will not lock you out of the machine.

| Machine | Backend | Port | Ruleset                        |
|---------|---------|------|--------------------------------|
| Mac 3   | A       | 3001 | `backend-a-isolation.pf.example` |
| Mac 4   | B       | 3002 | `backend-b-isolation.pf.example` |

## Apply (run on the backend machine)

```bash
# Mac 3 (Backend A). On Mac 4 use backend-b-isolation.pf.example.
sudo pfctl -a com.team1/isolation -f firewall/backend-a-isolation.pf.example
sudo pfctl -e        # enable pf if not already enabled (ignore "already enabled")

# Confirm the rule is loaded:
sudo pfctl -a com.team1/isolation -s rules
```

## Demonstrate

```bash
# From the EDGE (Mac 2) — still works:
curl -s http://10.7.28.78:3001/api/status        # Backend A answers

# From a CLIENT Mac (e.g. Mac 1) — now blocked (times out / no route):
curl -s --max-time 5 http://10.7.28.78:3001/api/status   # hangs then fails
nc -vz -w 5 10.7.28.78 3001                               # Operation timed out

# The service by NAME through the edge still works from any client:
curl -s https://app.team1.test:8443/api/status            # OK
```

Expected: the edge reaches the backend directly; a client cannot reach port
3001/3002 directly, but can still use the service through `app.team1.test`.

## Roll back (restore original configuration after the demo)

```bash
# Flush just our anchor:
sudo pfctl -a com.team1/isolation -F rules

# And/or reload the default system ruleset:
sudo pfctl -f /etc/pf.conf

# Optionally disable pf entirely (if you enabled it only for this demo):
sudo pfctl -d
```

> Keep a rollback copy: the original system ruleset is `/etc/pf.conf`.
> `sudo pfctl -f /etc/pf.conf` always restores it.
