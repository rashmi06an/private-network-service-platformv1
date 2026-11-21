# Phase 2 Demo Runbook — Team Scout Regiment

Exact commands for the Phase 2 extensions and the Review-2 demonstration.
Picks up from the Phase 1 runbook ([demo-runbook.md](demo-runbook.md)); the base
system (DNS, edge, backends) must already be running.

## Addresses (Phase 2 — DHCP reassigned these from Phase 1; see [network-inventory.md](network-inventory.md))

| Host  | Role (P1)   | Phase 2 role         | Phase 1 IP   | Phase 2 IP    |
|-------|-------------|----------------------|--------------|---------------|
| Mac 1 | primary DNS | TTL / record change  | `10.7.17.21` | `10.7.27.145` |
| Mac 2 | nginx edge  | HA failover (primary)| `10.7.7.9`   | `10.7.25.25`  |
| Mac 3 | Backend A   | **standby edge** + firewall A | `10.7.21.15` | `10.7.28.78` |
| Mac 4 | Backend B   | **backup DNS** + firewall B   | `10.7.23.47` | `10.7.27.247` |

DNS records (Phase 2): `app` / `api` / `ttl.team1.test → 10.7.25.25` (Mac 2), TTL `30`.

---

## Pre-demo startup (Phase 2 additions)

```bash
# Mac 2 — load the Phase 2 edge config (HA failover)
#   copy edge/nginx-phase2.conf.example -> /opt/homebrew/etc/nginx/nginx.conf
sudo nginx -t && sudo nginx -s reload

# Mac 4 — start the BACKUP DNS (second dnsmasq)
#   copy dns/backup-dnsmasq.conf.example -> /opt/homebrew/etc/dnsmasq.conf
sudo brew services start dnsmasq

# Clients — DNS list = 10.7.27.145 (primary) then 10.7.27.247 (backup)
```

---

## Extension A — Backup DNS failover

```bash
# From a client — both resolvers answer:
scripts/test-backup-dns.sh
# or manually:
dig @10.7.27.145 app.team1.test     # primary
dig @10.7.27.247 app.team1.test     # backup

# Stop the PRIMARY on Mac 1:
sudo brew services stop dnsmasq        # (on Mac 1)

# From a client — primary down, backup still answers (split-DNS: use @server, not bare dig):
dig @10.7.27.145 app.team1.test              # times out (primary down)
dig @10.7.27.247 app.team1.test              # 10.7.25.25 (backup answers)
dscacheutil -q host -a name app.team1.test   # 10.7.25.25 (system fell back to backup)

# Restore on Mac 1:
sudo brew services start dnsmasq
```
📸 `evidence/phase2/backup-dns/` — A1 both-resolve, A2 Mac4 lsof, A3 primary-down+backup-answers, A4 https-ok.

> **Split-DNS:** a bare `dig app.team1.test` goes to the global resolver (8.8.8.8) and
> returns NXDOMAIN — always name the server with `@`, or use `dscacheutil`.

## Extension B — TTL and controlled record change

```bash
scripts/test-dns-ttl.sh            # TTL counts 30 -> down (ttl.team1.test)

# On Mac 1 AND Mac 4: change ttl.team1.test to 10.7.28.78 on BOTH servers, then restart each.
#   sudo sed -i '' 's@ttl.team1.test/10.7.25.25@ttl.team1.test/10.7.28.78@' <dnsmasq.conf>
#   sudo brew services restart dnsmasq
# (Change BOTH — else the backup keeps serving the old IP and the flush shows no change.)

# From a client:
dig @10.7.27.145 ttl.team1.test                # NEW ip immediately (authoritative, skips cache)
dscacheutil -q host -a name ttl.team1.test     # OLD ip until 30s TTL expires or you flush
sudo dscacheutil -flushcache; sudo killall -HUP mDNSResponder   # immediate switch
dscacheutil -q host -a name ttl.team1.test     # NEW ip now
```
📸 `evidence/phase2/ttl/` — B1 TTL-30, B2 authoritative-new, B3 cached-then-expiry, B4 flush before/after.

## Extension C — Service isolation (firewall)

```bash
# On Mac 3:  sudo pfctl -a com.team1/isolation -f firewall/backend-a-isolation.pf.example && sudo pfctl -e
# On Mac 4:  sudo pfctl -a com.team1/isolation -f firewall/backend-b-isolation.pf.example && sudo pfctl -e

# From a CLIENT:
scripts/test-backend-isolation.sh      # direct :3001/:3002 blocked; by-name via edge works
# From the EDGE (Mac 2): direct curl to :3001/:3002 still succeeds.

# Roll back: sudo pfctl -a com.team1/isolation -F rules ; sudo pfctl -f /etc/pf.conf
```
📸 `evidence/phase2/isolation/` — blocked-from-client, works-from-edge, by-name-ok.

## Extension D — HA failover

```bash
scripts/test-ha-failover.sh            # both up: A/B alternate
# Stop Backend A on Mac 3 (Ctrl-C), re-run: all HTTP 200, X-Backend: B (no 502)
# Restart Backend A: A/B alternate again
```
📸 `evidence/phase2/ha-failover/` — balanced, A-down-all-B-200, rebalanced.

## Extension E — Controlled edge migration (DNS cutover)

```bash
# Mac 3 — start the standby edge:
#   copy edge/standby-nginx.conf.example -> /opt/homebrew/etc/nginx/nginx.conf
sudo nginx -t && sudo nginx

# Baseline from a client:
curl -sI https://app.team1.test:8443/api/status | grep -i x-edge   # primary-mac2

# Mac 1 — repoint app.team1.test to the standby:
#   address=/app.team1.test/10.7.28.78   then: sudo brew services restart dnsmasq

# From a client, after flushing / TTL expiry:
sudo dscacheutil -flushcache; sudo killall -HUP mDNSResponder
curl -sI https://app.team1.test:8443/api/status | grep -i x-edge   # standby-mac3

# Restore: set the record back to 10.7.25.25, restart dnsmasq.
```
📸 `evidence/phase2/edge-migration/` — x-edge before, record change, x-edge after.

## Extension F — Faculty-injected fault (diagnose live)

```bash
dig @10.7.27.145 app.team1.test                 # 1. DNS layer (name the server; bare dig hits 8.8.8.8)
nc -vz 10.7.25.25 8443                            # 2. TCP layer
curl -vI https://app.team1.test:8443/           # 3. TLS/HTTP layer
curl -s http://10.7.28.78:3001/api/status       # 4a. Backend A direct
curl -s http://10.7.27.247:3002/api/status       # 4b. Backend B direct
```
Narrate the hypothesis at each step. Partial credit is for correct methodology.
📸 `evidence/phase2/troubleshooting/` — your diagnosis notes/screens on demo day.
