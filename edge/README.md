# nginx edges

Mac 2 primary: 10.7.25.25; Mac 3 standby: 10.7.28.78. Both serve 8080 (redirect)
and 8443 (TLS). Current configs share the same upstream addresses, timeouts and
passive retry policy; X-Edge identifies the host. The shared upstream zone keeps
failure and round-robin state consistent across worker processes.

After installing valid hostname leaf cert/key and the public CA trust:

```bash
scripts/apply-edge.sh primary   # Mac 2 only
# scripts/apply-edge.sh standby # Mac 3 only, during Extension E
scripts/test-https.sh
scripts/test-load-balancing.sh
```

Apply helpers keep timestamped config backups under `.local-state/` and validate
before replacement. A running daemon reloads; an absent daemon starts. For manual
rollback, restore the saved nginx.conf/tls.conf paths printed by the helper, run
`sudo nginx -t`, then reload. Never restore a private key from Git.

`nginx.conf.example` retains historical Phase 1 IP addresses; the normal current
deployment uses `nginx-phase2.conf.example`. Historical screenshots can have older
cache behavior. Current cache demo is `/api/cache-demo`, not `/api/status`.
