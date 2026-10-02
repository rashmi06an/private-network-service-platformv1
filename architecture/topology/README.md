# Network Topology — Team 1

All four Macs are connected to the **same private Wi-Fi / LAN**. Fill in the
real private IPs (from `docs/network-inventory.md`) where marked `TBD`.

```
                    Private Wi-Fi / LAN (same subnet)
   ┌──────────────┬──────────────────┬──────────────┬──────────────┐
   │              │                  │              │              │
┌──┴───┐      ┌───┴────┐         ┌────┴───┐      ┌───┴────┐
│ Mac 1 │      │ Mac 2  │         │ Mac 3  │      │ Mac 4  │
│ DNS + │      │ Edge   │         │Backend │      │Backend │
│Client │      │ nginx  │         │  A     │      │  B +   │
│dnsmasq│      │ TLS/LB │         │ :3001  │      │Client  │
│  :53  │      │:443/80 │         │        │      │ :3002  │
└───────┘      └────────┘         └────────┘      └────────┘
 Rashmi        Samiksha          Shubhaang         Ankit
  TBD IP        TBD IP            TBD IP            TBD IP
```

## Roles and cloud equivalents

| Machine | Member    | Role                      | Service(s)          | Cloud equivalent          |
|---------|-----------|---------------------------|---------------------|---------------------------|
| Mac 1   | Rashmi    | Private DNS + Test Client | dnsmasq (:53/UDP)   | Managed DNS (Route 53)    |
| Mac 2   | Samiksha  | Edge / Reverse Proxy + LB | nginx, TLS (:443)   | Cloud load balancer / CDN |
| Mac 3   | Shubhaang | Backend Server A          | Flask REST (:3001)  | App server instance A     |
| Mac 4   | Ankit     | Backend Server B + Client | Flask REST (:3002)  | App server instance B     |

## Reachability

Verify every pair of machines can `ping` each other before anything else.
Capture the output into `evidence/phase1/network/`.
