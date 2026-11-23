# Phase 2 historical screenshot index

These are historical screenshots, not a complete current acceptance suite. The table
describes actual contents even where an old filename is misleading. New proof goes
in [verification](../verification/) and the [acceptance ledger](../../reports/verification-status.json).

| Screenshot | Actual content / limit |
|---|---|
| [A1-both-resolvers-and-backends-mac3.png](backup-dns/A1-both-resolvers-and-backends-mac3.png) | Mac 3: primary=.25.25, backup=.28.78 (different); backend/HTTPS success. Does not prove synchronized DNS. |
| [A2-backup-dns-listening-mac4.png](backup-dns/A2-backup-dns-listening-mac4.png) | Mac 4 backup UDP/TCP 53 listeners; also shows config-file edits, not proof of final synchronized answers. |
| [A2b-mac4-backend-and-backup-dns.png](backup-dns/A2b-mac4-backend-and-backup-dns.png) | Despite filename, Mac 2 balanced A/B followed by B-only successful requests while A fails. Useful D stage evidence. |
| [A3-note-bare-dig-hits-public-nxdomain.png](backup-dns/A3-note-bare-dig-hits-public-nxdomain.png) | Bare dig uses8.8.8.8 and getsNXDOMAIN; diagnostic split-DNS note, not private-resolver failover. |
| [A3-primary-down-backup-answers-mac2.png](backup-dns/A3-primary-down-backup-answers-mac2.png) | Primary timeout; backup=.28.78 with TTL 0; system=.25.25. Fresh OS backup selection is not established. |
| [primary-dns-listening-mac1.png](backup-dns/primary-dns-listening-mac1.png) | Primary UDP/TCP 53 listener and correct app/api answers; stop/start commands also present. |
| [primary-dns-tcpdump-and-https-mac1.png](backup-dns/primary-dns-tcpdump-and-https-mac1.png) | Team-domain DNS query/answer visible; shown earlier HTTPS block uses an IP host. Do not count it as by-name outage proof. |
| [setup-mac1-dig-tests.png](backup-dns/setup-mac1-dig-tests.png) | Primary stop/timeout/start/answer stages, without a synchronized fresh client/backup trace. |
| [setup-mac1-dns-service-checks.png](backup-dns/setup-mac1-dns-service-checks.png) | Initial timeouts/service and privilege troubleshooting; preserve as diagnostic, not PASS. |
| [setup-mac1-ip-fix-dhcp-rebind.png](backup-dns/setup-mac1-ip-fix-dhcp-rebind.png) | Old lease/config diagnosis and corrections; includes failed lookups during setup. |
| [E2-standby-https-xedge-and-dns-mac2.png](edge-migration/E2-standby-https-xedge-and-dns-mac2.png) | Both DNS servers/system lookup=.28.78; normal by-name HTTPS200, standby header, connected IP=.28.78. Positive cutover exhibit. |
| [E2b-standby-https-both-backends-mac2.png](edge-migration/E2b-standby-https-both-backends-mac2.png) | Standby A/B200 with --resolve. Proves connectivity and trust, bypasses DNS for this test. |
| [E3-cutover-client-connected-ip-mac2.png](edge-migration/E3-cutover-client-connected-ip-mac2.png) | Ends at primary connected IP=.25.25 while primary/backup DNS disagree. Restoration is incomplete; not a clean NEW-standby exhibit. |
| [D1-load-balanced-then-A-down.png](ha-failover/D1-load-balanced-then-A-down.png) | Despite filename, Mac 4 Backend B listener/status and backup DNS=.25.25. Not a load-balancing/A-down trace. |
| [D2-all-B-then-recovered.png](ha-failover/D2-all-B-then-recovered.png) | B-only200 then recovered output includesA/B after 11 seconds; useful D proof. |
| [C1-pf-rules-mac3-backend-a.png](isolation/C1-pf-rules-mac3-backend-a.png) | Mac 3 backup, reachable com.apple/team1_phase2 anchor, allow/block rules, PF token; also both scoped DNS servers. |
| [C2-pf-rules-mac4-backend-b.png](isolation/C2-pf-rules-mac4-backend-b.png) | Mac 4 rules plus actual anchor clear and enable-token release. Existing rollback evidence. |
| [C3-client-blocked-mac1.png](isolation/C3-client-blocked-mac1.png) | Blocked attempts followed later by successful direct backend responses (restored stage). Label the states explicitly. |
| [C3b-client-blocked-timeouts-mac1.png](isolation/C3b-client-blocked-timeouts-mac1.png) | Both backend timeouts and later both direct responses; also app cutover/restoration commands. Rollback outcome is embedded. |
| [C4-edge-reaches-backends-mac2.png](isolation/C4-edge-reaches-backends-mac2.png) | Mac 2 direct HTTP/200 with A/B identity; permitted-source proof. |
| [B1-ttl30-record-countdown-mac1.png](ttl/B1-ttl30-record-countdown-mac1.png) | TTL 30 and record edit commands; not a client TTL countdown. |
| [B2-authoritative-change-new-ip-mac1.png](ttl/B2-authoritative-change-new-ip-mac1.png) | app record cutover/new answer and TTL editing/restart commands; not timed client expiry. |
| [B3-mac1-app-and-ttl-records.png](ttl/B3-mac1-app-and-ttl-records.png) | Two different names: app=.25.25, ttl=.28.78, TTL 30. Not OLD→NEW for one client record. |
| [B3b-dscacheutil-ttl-mac1.png](ttl/B3b-dscacheutil-ttl-mac1.png) | System lookup sees NEW; old cached answer then timed expiry is absent. |
| [B4-attempt1-diagnostic-mac2.png](ttl/B4-attempt1-diagnostic-mac2.png) | Before and after flush remain.25.25. Unsuccessful transition proof. |
| [B4-attempt2-diagnostic-mac2.png](ttl/B4-attempt2-diagnostic-mac2.png) | Before and after flush remain.28.78. Unsuccessful transition proof. |
| [B4-note-backup-missing-ttl-nxdomain-mac4.png](ttl/B4-note-backup-missing-ttl-nxdomain-mac4.png) | Backup TTL record NXDOMAIN at that time; a DNS synchronization defect. |
| [dns-query-response-app-team1.png](wireshark/dns-query-response-app-team1.png) | Project DNS query/response: Mac 2↔Mac 1; ephemeral port61827↔53. |
| [dns-split-behavior-public-nxdomain.png](wireshark/dns-split-behavior-public-nxdomain.png) | Private A answers plus other DNS queries/public forwarding in the historical live config. Not the exact new scoped-only DNS template. |
| [tls-handshake-clienthello-serverhello.png](wireshark/tls-handshake-clienthello-serverhello.png) | TLS 1.3 ClientHello/ServerHello/CCS/encrypted records, ports56853↔8443. Certificate not decoded. |

The two previously requested optional internal-HTTP/RST PNGs are not attached; do
not label them captured. Actual faculty fault evidence is added only when administered.
Use the new verification ledger rather than the historical filename checklist.
