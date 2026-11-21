# Client DNS Setup

> **Note on addresses:** the LAN IPs differ between Phase 1 and Phase 2 because
> DHCP handed out new leases between the two sessions. The **domain names stayed
> the same** — which is the whole point of DNS. Both address sets are listed in
> [docs/network-inventory.md](../docs/network-inventory.md).

| Role             | Machine        | Phase 1 IP   | Phase 2 IP    |
|------------------|----------------|--------------|---------------|
| Primary DNS      | Mac 1 (Rashmi) | `10.7.17.21` | `10.7.27.145` |
| Backup DNS       | Mac 4 (Ankit)  | —            | `10.7.27.247` |
| Edge (resolves to)| Mac 2 (Samiksha) | `10.7.7.9` | `10.7.25.25`  |

## Phase 1 — primary resolver only

DNS Server (Mac 1): `10.7.17.21`
System Settings → Network → (Wi-Fi) Details → DNS → add `10.7.17.21`.

## Phase 2 / Extension A — primary + backup resolver

Add a **second** DNS server so clients keep resolving if the primary stops.

| Order     | Server (Phase 2) | Machine          |
|-----------|------------------|------------------|
| Primary   | `10.7.27.145`    | Mac 1 (Rashmi)   |
| Backup    | `10.7.27.247`    | Mac 4 (Ankit)    |

System Settings → Network → (Wi-Fi) Details → DNS → list **both**, primary first:

```
10.7.27.145
10.7.27.247
```

macOS tries the first resolver; if it does not answer, it falls back to the second.

Clients configured this way: Mac 2 (Samiksha), Mac 3 (Shubhaang), Mac 4 (Ankit).

Required DNS records (served identically by Mac 1 and Mac 4):

```
app.team1.test -> 10.7.25.25
api.team1.test -> 10.7.25.25
ttl.team1.test -> 10.7.25.25   (TTL demo record)
```

## Split-DNS note (how these Macs are actually set up)

The clients resolve the private zone through `/etc/resolver/team1.test`, which lists
the team DNS servers. So only `*.team1.test` goes to the team DNS; everything else
goes to the normal internet resolver (e.g. `8.8.8.8`).

**Consequence:** `dig app.team1.test` **without `@server`** uses the *global* resolver
(`8.8.8.8`), which does not know `.test` → it returns **NXDOMAIN**. That is expected.
To query the team DNS, either name the server explicitly (`dig @10.7.27.145 …`) or use
the system resolver path (`dscacheutil -q host -a name …`, or a browser/curl), which
honours `/etc/resolver/team1.test`.

## Verification

```bash
# Primary resolver (explicit)
dig @10.7.27.145 app.team1.test
# Backup resolver (explicit, same answer)
dig @10.7.27.247 app.team1.test
# End-to-end via the system resolver (honours /etc/resolver)
dscacheutil -q host -a name app.team1.test
```

Expected: all resolve to `10.7.25.25` (the Phase 2 private IP of Mac 2).

## Failover test (Extension A)

```bash
# On Mac 1 — stop the PRIMARY DNS service:
sudo brew services stop dnsmasq

# From a client — show the primary is down but the backup still answers:
dig @10.7.27.145 app.team1.test     # times out (primary down)
dig @10.7.27.247 app.team1.test     # 10.7.25.25  (backup answers)
dscacheutil -q host -a name app.team1.test   # 10.7.25.25 (system fell back to backup)

# Restore afterwards (on Mac 1):
sudo brew services start dnsmasq
```

> Do **not** use a bare `dig app.team1.test` here — it goes to the global resolver
> (`8.8.8.8`) and returns NXDOMAIN, which does not prove anything about failover.

**DNS failure vs application failure:** stopping dnsmasq breaks *name resolution*
(you cannot find the IP). It is different from a backend being down, where the
name still resolves but the *service* behind it returns an error.
