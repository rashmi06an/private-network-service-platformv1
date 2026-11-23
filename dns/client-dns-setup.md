# Scoped DNS on client Macs

Run on at least Mac 2 and Mac 3; Mac 1 and Mac 4 can also act as clients:

```bash
scripts/client-dns.sh install
cat /etc/resolver/team1.test
scutil --dns | sed -n '/domain *: team1.test/,+8p'
```

The file contains both 10.7.27.145 and 10.7.27.247. macOS resolver selection is
system-managed; do not infer that it used the backup just from a cached answer.
Prove failover with a stopped primary, a fresh system lookup, successful normal
HTTPS and a query observed on Mac 4.

```bash
dig @10.7.27.145 app.team1.test
dig @10.7.27.247 app.team1.test
dscacheutil -q host -a name app.team1.test
/usr/bin/curl --noproxy '*' -i https://app.team1.test:8443/api/status
```

`dig` without @server uses the global resolver and does not follow macOS scoped
resolution. NXDOMAIN from a public resolver is not evidence that private DNS is
down. The normal app/browser/curl uses system resolution; do not use --resolve as
proof of that DNS path. A direct server query is useful separately for diagnosis.

Rollback the exact prior scoped file with `scripts/client-dns.sh restore`.
Temporary client-cache use in the TTL cutover test backs up/restores the same
file within that experiment; it does not replace the normal two-server setup.
