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

## Live verification note

The Phase 2 IPs were supplied again on 22 November 2026. Prefix, gateway,
interface and MAC values in the table are historical measurements until each
member records the new preflight. Private Wi-Fi MAC values may rotate; record
observed values rather than assuming permanence. Early Phase 1 dig screenshots
used an additional DNS lease 10.7.21.14, explicitly historical.

### 23 November current Mac2 observation

[Recorded Mac2 preflight](../evidence/verification/R0-mac2-20261123T045726Z.txt)
confirms en0,10.7.25.25/19, gateway10.7.0.1 and MAC8e:f2:4f:b4:75:a5. Both
pings to Mac3 andMac4 replied; both pings to Mac1 timed out, making preflight
exit1. [A separate transport check](../evidence/verification/R0-primary-dns-transport-20261123T045908Z.txt)
shows Mac1 still answers the expected DNS record over UDP and accepts TCP53.
The ICMP behavior needs diagnosis; this is not a completed twelve-ping acceptance.
The remaining three current inventories are still pending.

### Remaining inventories and ICMP diagnosis

The [team-supplied observations](../evidence/verification/2026-11-23-three-mac-inventory-observations.json)
confirm all three remaining IP/MAC/en0/prefix/gateway assignments at05:01 UTC.
This file is a structured transcription of pasted outputs, not an original recorder
log. All twelve directed ping outcomes are now observed: nine pass, three fail,
with every failure directed at Mac1. The [Mac1 setting readout](../evidence/verification/R0-mac1-stealth-20261123T050104Z.txt)
shows stealth ON. A targeted stealth-off change and inbound retest remain necessary;
the original setting can be restored after the lab with
`sudo /usr/libexec/ApplicationFirewall/socketfilterfw --setstealthmode on`.
Keep the Application Firewall's other settings unchanged.

[Mac3's scoped DNS setup](../evidence/verification/R2-mac3-client-dns-20261123T050122Z.txt)
now joins Mac2 as the second verified dual-resolver client. Mac1's localhost-only
private setting and Mac4's old10.7.17.21 setting need `scripts/client-dns.sh install`.
Inspect Mac4's service-level DNS independently; the private-zone readout alone is
not proof of its complete global resolver configuration.

### Managed-Mac restriction and remaining service DNS

The [05:05–05:06 rechecks](../evidence/verification/2026-11-23-managed-stealth-and-dns-rechecks.json)
show that the [stealth setter](../evidence/verification/R0-mac1-stealth-off-20261123T050558Z.txt)
printed a managed-Mac refusal while returning exit0; the independent
[readback](../evidence/verification/R0-mac1-stealth-confirm-20261123T050558Z.txt)
still reports ON. The off/retest correction above was therefore **not applied**.
Inventory acceptance remains open pending a permitted IT/faculty change or explicit
assessment exception. Other experiments can proceed using verified DNS/TCP service
reachability. Do not report nine successful directions as twelve.

Canonical private-zone installation now also passed on Mac1 andMac4, so all four
clients have both current resolver addresses. Mac4's separate Wi-Fi DNS list still
contains obsolete10.7.17.21 followed by8.8.8.8. Preserve its original list and remove
the stale entry while retaining the existing public resolver; verify readback rather
than relying only on a setter's exit code.
