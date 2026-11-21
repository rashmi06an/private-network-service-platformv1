# Phase 2 — Sequential Commands per Mac (for screenshots)

Run top-to-bottom. Each block says **which Mac** runs it. 📸 = take a screenshot.
Save each screenshot into the `evidence/phase2/<folder>/` shown.

Addresses: Mac1 `10.7.27.145` (DNS) · Mac2 `10.7.25.25` (edge) · Mac3 `10.7.28.78` (Backend A / standby edge) · Mac4 `10.7.27.247` (Backend B / backup DNS)

---

## STEP 0 — Base system up (do first, on each Mac)

**Mac 3 — Backend A**
```bash
cd backend-a && source venv/bin/activate && python3 app.py      # listens 0.0.0.0:3001
```
**Mac 4 — Backend B**
```bash
cd backend-b && source venv/bin/activate && python3 app.py      # listens 0.0.0.0:3002
```
**Mac 1 — primary DNS**
```bash
sudo brew services start dnsmasq
```
**Mac 2 — edge (Phase 2 config with HA failover)**
```bash
# copy edge/nginx-phase2.conf.example -> /opt/homebrew/etc/nginx/nginx.conf first
sudo nginx -t && sudo nginx
```

---

## EXTENSION A — Backup DNS  →  evidence/phase2/backup-dns/

**Mac 4 — start the backup DNS**
```bash
# copy dns/backup-dnsmasq.conf.example -> /opt/homebrew/etc/dnsmasq.conf first
sudo brew services start dnsmasq
```
**Mac 1 (client) — both resolvers answer**
```bash
dig @10.7.27.145 app.team1.test      # primary
dig @10.7.27.247 app.team1.test      # backup
```
📸 `both-resolvers.png` (both show 10.7.25.25)

**Mac 1 — stop the primary DNS**
```bash
sudo brew services stop dnsmasq
```
**A client (with both resolvers / `/etc/resolver`) — primary down, backup answers**
```bash
dig @10.7.27.145 app.team1.test              # times out (primary down)
dig @10.7.27.247 app.team1.test              # 10.7.25.25 (backup answers)
dscacheutil -q host -a name app.team1.test   # 10.7.25.25 (system fell back to backup)
```
📸 `A3-primary-stopped-backup-answers.png`
> Do NOT use bare `dig app.team1.test` — split-DNS sends it to 8.8.8.8 → NXDOMAIN.

**Mac 1 — restore**
```bash
sudo brew services start dnsmasq
```

---

## EXTENSION B — TTL + record change  →  evidence/phase2/ttl/

**Any client — TTL counts down** (name the server; bare dig hits 8.8.8.8)
```bash
dig @10.7.27.145 +noall +answer ttl.team1.test ; sleep 5
dig @10.7.27.145 +noall +answer ttl.team1.test ; sleep 5
dig @10.7.27.145 +noall +answer ttl.team1.test
```
📸 `B1-ttl30-countdown.png` (TTL 30 → ~25 → ~20)

**Mac 1 AND Mac 4 — change the record to 10.7.28.78 on BOTH servers**
```bash
# Mac 1:  sudo sed -i '' 's@ttl.team1.test/10.7.25.25@ttl.team1.test/10.7.28.78@' /opt/homebrew/etc/dnsmasq.conf
# Mac 4:  same sed on its /opt/homebrew/etc/dnsmasq.conf
sudo brew services restart dnsmasq        # on each
```
> Change BOTH — else the backup keeps serving 10.7.25.25 and the flush shows no change.

**Any client — authoritative vs cached**
```bash
dig @10.7.27.145 ttl.team1.test              # NEW ip immediately (authoritative)
dscacheutil -q host -a name ttl.team1.test   # OLD ip until 30s TTL expires
```
📸 `B2-authoritative-new-ip.png` + `B3-client-cached-then-expiry.png`

**Any client — flush and switch instantly**
```bash
dscacheutil -q host -a name ttl.team1.test   # BEFORE: old 10.7.25.25
sudo dscacheutil -flushcache; sudo killall -HUP mDNSResponder
dscacheutil -q host -a name ttl.team1.test   # AFTER: new 10.7.28.78
```
📸 `B4-manual-flush-before-after.png`

**Mac 1 and Mac 4 — restore ttl.team1.test to 10.7.25.25 on both**
```bash
# edit each dnsmasq.conf back to:  address=/ttl.team1.test/10.7.25.25
sudo brew services restart dnsmasq
```

---

## EXTENSION C — Service isolation  →  evidence/phase2/isolation/

**Mac 3 — apply firewall (Backend A)**
```bash
sudo pfctl -a com.team1/isolation -f firewall/backend-a-isolation.pf.example
sudo pfctl -e
```
**Mac 4 — apply firewall (Backend B)**
```bash
sudo pfctl -a com.team1/isolation -f firewall/backend-b-isolation.pf.example
sudo pfctl -e
```
**Mac 1 (client) — direct access now BLOCKED**
```bash
curl -s --max-time 5 http://10.7.28.78:3001/api/status ; echo "exit=$?"
nc -vz -w 5 10.7.28.78 3001
```
📸 `blocked-from-client.png` (times out)

**Mac 2 (edge) — direct access still WORKS**
```bash
curl -s http://10.7.28.78:3001/api/status ; echo
curl -s http://10.7.27.247:3002/api/status ; echo
```
📸 `works-from-edge.png`

**Mac 1 (client) — by name through the edge still WORKS**
```bash
curl -s https://app.team1.test:8443/api/status ; echo
```
📸 `by-name-still-ok.png`

**Mac 3 and Mac 4 — roll back**
```bash
sudo pfctl -a com.team1/isolation -F rules
sudo pfctl -f /etc/pf.conf
```

---

## EXTENSION D — HA failover  →  evidence/phase2/ha-failover/

**Any client — both backends up (A/B alternate)**
```bash
for i in $(seq 1 8); do curl -s -D - https://app.team1.test:8443/api/status -o /dev/null | grep -i x-backend; done
```
📸 `balanced.png`

**Mac 3 — stop Backend A** (Ctrl-C in its terminal)

**Any client — service continues on B only, no 502**
```bash
for i in $(seq 1 8); do curl -s -o /dev/null -w "HTTP %{http_code}  " https://app.team1.test:8443/api/status; curl -s -D - https://app.team1.test:8443/api/status -o /dev/null | grep -i x-backend; done
```
📸 `backendA-down-all-B-200.png`

**Mac 3 — restart Backend A**
```bash
cd backend-a && source venv/bin/activate && python3 app.py
```
**Any client — rebalanced**
```bash
for i in $(seq 1 8); do curl -s -D - https://app.team1.test:8443/api/status -o /dev/null | grep -i x-backend; done
```
📸 `rebalanced.png`

---

## EXTENSION E — Edge migration (DNS cutover)  →  evidence/phase2/edge-migration/

**Mac 3 — start the standby edge**
```bash
# copy edge/standby-nginx.conf.example -> /opt/homebrew/etc/nginx/nginx.conf
# (copy Mac 2's certs/ folder to Mac 3 first so the cert matches the name)
sudo nginx -t && sudo nginx
```
**Any client — baseline: traffic goes to primary**
```bash
curl -sI https://app.team1.test:8443/api/status | grep -i x-edge     # primary-mac2
```
📸 `x-edge-primary.png`

**Mac 1 — repoint the name to the standby**
```bash
# edit dnsmasq.conf:  address=/app.team1.test/10.7.28.78
sudo brew services restart dnsmasq
```
📸 `record-change.png` (the edited line)

**Any client — after TTL/flush, traffic goes to standby**
```bash
sudo dscacheutil -flushcache; sudo killall -HUP mDNSResponder
curl -sI https://app.team1.test:8443/api/status | grep -i x-edge     # standby-mac3
```
📸 `x-edge-standby.png`

**Mac 1 — restore** (`address=` back to `10.7.25.25`, `restart dnsmasq`)
**Mac 3 — stop standby edge** (`sudo nginx -s stop`)

---

## EXTENSION F — Faculty fault (live on demo day)  →  evidence/phase2/troubleshooting/

Diagnose bottom-up, narrating each step:
```bash
dig @10.7.27.145 app.team1.test             # 1. DNS  — name resolves? right IP? (name the server)
nc -vz 10.7.25.25 8443                         # 2. TCP  — port reachable?
curl -vI https://app.team1.test:8443/        # 3. TLS/HTTP — handshake/cert ok?
curl -s http://10.7.28.78:3001/api/status    # 4a. Backend A direct
curl -s http://10.7.27.247:3002/api/status    # 4b. Backend B direct
```
📸 screenshots of your diagnosis + a note: what the fault was, which layer, how you fixed/isolated it.
