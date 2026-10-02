# Network Inventory

All machines on the same private LAN (`/19`, gateway `10.7.0.1`, interface `en0`).

| Machine | Member    | Role              | IPv4         | Prefix | Gateway    | Interface | MAC                 |
|---------|-----------|-------------------|--------------|--------|------------|-----------|---------------------|
| Mac 1   | Rashmi    | DNS + Test Client | `10.7.17.21` | `/19`  | `10.7.0.1` | `en0`     | `fe:cf:32:29:21:34` |
| Mac 2   | Samiksha  | Nginx + HTTPS/TLS | `10.7.7.9`   | `/19`  | `10.7.0.1` | `en0`     | `8e:f2:4f:b4:75:a5` |
| Mac 3   | Shubhaang | Backend A         | `10.7.21.15`  | `/19`  | `10.7.0.1` | `en0`     | `12:53:0c:44:d1:cb` |
| Mac 4   | Ankit     | Backend B         | `10.7.23.47` | `/19`  | `10.7.0.1` | `en0`     | `d2:f7:e1:53:a7:1f` |

## Service map

| Service              | Host  | IP:Port            |
|----------------------|-------|--------------------|
| Private DNS (dnsmasq)| Mac 1 | `10.7.17.21:53`    |
| nginx edge (HTTPS)   | Mac 2 | `10.7.7.9:8443`     |
| Backend A            | Mac 3 | `10.7.21.15:3001`   |
| Backend B            | Mac 4 | `10.7.23.47:3002`  |

## DNS records

| Name             | Resolves to          |
|------------------|----------------------|
| `app.team1.test` | `10.7.7.9` (Mac 2)   |
| `api.team1.test` | `10.7.7.9` (Mac 2)   |
