# Network Inventory

All machines on the same private LAN (`10.7.0.0/19`, gateway `10.7.0.1`, interface `en0`).

> **Why two IP columns?** The project ran across two sessions (Phase 1 and
> Phase 2). The Wi-Fi/DHCP server handed out **different leases** each time, so
> every machine's LAN IP changed between phases. The **MAC addresses and the
> domain names did not change** — clients kept using `app.team1.test` while the
> underlying IPs moved. This is exactly the real-world reason DNS exists, and it
> ties directly into the Phase 2 TTL / edge-cutover demonstrations.

## Machines

| Machine | Member    | Role                         | Phase 1 IPv4 | Phase 2 IPv4  | Prefix | Gateway    | Interface | MAC                 |
|---------|-----------|------------------------------|--------------|---------------|--------|------------|-----------|---------------------|
| Mac 1   | Rashmi    | Primary DNS + Test Client    | `10.7.17.21` | `10.7.27.145` | `/19`  | `10.7.0.1` | `en0`     | `fe:cf:32:29:21:34` |
| Mac 2   | Samiksha  | nginx Edge + HTTPS/TLS + LB  | `10.7.7.9`   | `10.7.25.25`  | `/19`  | `10.7.0.1` | `en0`     | `8e:f2:4f:b4:75:a5` |
| Mac 3   | Shubhaang | Backend A (+ standby edge P2)| `10.7.21.15` | `10.7.28.78`  | `/19`  | `10.7.0.1` | `en0`     | `12:53:0c:44:d1:cb` |
| Mac 4   | Ankit     | Backend B (+ backup DNS P2)  | `10.7.23.47` | `10.7.27.247` | `/19`  | `10.7.0.1` | `en0`     | `d2:f7:e1:53:a7:1f` |

## Service map

| Service                 | Host  | Phase 1 IP:Port    | Phase 2 IP:Port     |
|-------------------------|-------|--------------------|---------------------|
| Primary DNS (dnsmasq)   | Mac 1 | `10.7.17.21:53`    | `10.7.27.145:53`    |
| Backup DNS (dnsmasq, P2)| Mac 4 | —                  | `10.7.27.247:53`    |
| nginx edge (HTTPS)      | Mac 2 | `10.7.7.9:8443`    | `10.7.25.25:8443`   |
| Standby edge (nginx, P2)| Mac 3 | —                  | `10.7.28.78:8443`   |
| Backend A               | Mac 3 | `10.7.21.15:3001`  | `10.7.28.78:3001`   |
| Backend B               | Mac 4 | `10.7.23.47:3002`  | `10.7.27.247:3002`  |

## DNS records

| Name             | Phase 1 resolves to | Phase 2 resolves to  | Notes                          |
|------------------|---------------------|----------------------|--------------------------------|
| `app.team1.test` | `10.7.7.9` (Mac 2)  | `10.7.25.25` (Mac 2) | Main entry point               |
| `api.team1.test` | `10.7.7.9` (Mac 2)  | `10.7.25.25` (Mac 2) | Same edge                      |
| `ttl.team1.test` | —                   | `10.7.25.25` (Mac 2) | Phase 2 TTL / cutover demo (30s TTL) |

During the Phase 2 edge-migration demo (Extension E), `app.team1.test` /
`ttl.team1.test` are temporarily repointed from `10.7.25.25` (Mac 2) to
`10.7.28.78` (Mac 3 standby edge), then restored.

## Reviewed current measurements - 23 November 2026

All four inventories have current IP/MAC/en0, /19 and gateway10.7.0.1 measurements.
[Mac2 original](../evidence/verification/R0-mac2-20261123T045726Z.txt) and
[other three transcribed inventories](../evidence/verification/2026-11-23-three-mac-inventory-observations.json)
retain acquisition times, observed fields and actual ping results.

| Ping source → destination | Mac1 | Mac2 | Mac3 | Mac4 |
|---|---|---|---|---|
| Mac1 | — | 2/2 | 2/2 | 2/2 |
| Mac2 | 0/2 | — | 2/2 | 2/2 |
| Mac3 | 0/2 | 2/2 | — | 2/2 |
| Mac4 | 0/2 | 2/2 | 2/2 | — |

Nine of12 directed probes succeed; all three failed directions target Mac1.
Its [stealth readback](../evidence/verification/R0-mac1-stealth-confirm-20261123T050558Z.txt)
remains ON. The managed Mac refused the command-line change despite exit0;
no successful GUI change or permitted exception was supplied. Preserve this
measured limitation. DNS UDP/TCP service success does not prove ICMP success.
No broad firewall disable is part of the submitted setup.

All four clients now have the two current private resolvers in their scoped
team1.test configuration. Mac4's obsolete service-level DNS entry was removed;
its [final Wi-Fi readback](../evidence/verification/2026-11-23-mac4-wifi-dns-final-readback.txt)
is8.8.8.8. These supersede the older localhost-only/stale-address observations.

The team ended further collection; the strict directed-ping acceptance item remains
open. IP leases and private Wi-Fi MAC addresses can change between sessions.
