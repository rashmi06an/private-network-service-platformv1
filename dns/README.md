# Primary and backup private DNS

Mac 1 10.7.27.145 and Mac 4 10.7.27.247 use the Phase 2 configs in this directory.
Both read the same project-records format from `/opt/homebrew/etc/team1-project.hosts`.
Normal records are in [project.hosts](project.hosts). TTL is 30 seconds.

```bash
scripts/setup-dns.sh primary  # Mac 1 only
# scripts/setup-dns.sh backup # Mac 4 only
scripts/test-backup-dns.sh both-up
```

The setup helper backs up existing files, stops the Homebrew instance, and refuses
an unrelated/manual port-53 listener. Stop the identified old manual instance on
Mac 4 in its own terminal before migration; do not use killall.

For a controlled record update on EACH resolver:

```bash
scripts/dns-record.sh ttl 10.7.28.78
scripts/dns-record.sh ttl 10.7.25.25   # restore
```

This updates the hosts data and sends SIGHUP to the verified service PID. dnsmasq
does not reread all address= configuration on HUP; the addn-hosts approach is used
deliberately to make synchronized changes quick and reproducible.

Only the project zone goes to these resolvers. The configs do not forward public
names; normal internet DNS remains in macOS's existing global configuration.
See [client setup](client-dns-setup.md), [commands](../docs/team-commands.md), and
[actual TTL experiments](../docs/ttl-experiments.md).
