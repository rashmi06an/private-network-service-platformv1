# Source fixes and reviewed acceptance

Final package review:23November2026. Collection ended at the team's request;
[the ledger](../reports/verification-status.json) retains observed limits.

| Audit ID | Implemented correction | Reviewed status |
|---|---|---|
| F01 | Real caching resolver and synchronized TTL schedule | Live natural expiry31.49s and restore verified |
| F02 | Separate explicit before-expiry flush | Live manual flush5.25s and restore verified |
| F03 | Synchronized DNS data, dual clients, outage/fresh lookup/receipt | Live controlled failover and restoration verified |
| F04 | Scheduled old/fresh/new cutover and both-server restore | Standby trust/fresh-new/restore verified; concurrent cached-old/convergence incomplete |
| F05 | Reachable narrow PF anchor and counters | Both hosts applied; edge allowed/client denied verified |
| F06 | Owned PF token and unchanged-main-rule rollback | Both hosts restored; other owner's enabled PF preserved |
| F07 | C rollback boundary / optional two-edge policy | Required C rollback verified before standby preflight |
| F08 | X-Edge preserved for all endpoints | Primary/standby runtime headers verified |
| F09 | Shared cache body/ETag and conditional304 | Both current backends and trusted edge304 verified |
| F10 | Executable shell helpers | Source/executable checks; actual clone invocations observed |
| F11 | Assertions reject wrong HTTP/identity/DNS | Regression fixtures and real failed attempts retained |
| F12 | Capture guide and actual saved-file gate | 57-packet original binary received; actual frame/socket index verified |
| F13 | Controlled TLS1.2 / TLS1.3 visibility explanation | Visible TLS1.2 Certificate frames13/38 and matching trusted client requests verified |
| F14 | Completion claims tied to actual results | Reports distinguish verified, historical and incomplete |
| F15 | Historical screenshots indexed by actual content | Original main PNGs retained; gallery and integrity report included |
| F16 | Four current inventories / directed ping checks | All inventories and12 directed successes verified across baseline and three repaired incoming directions |
| F17 | Historical leases / wrong-client DNS distinction | Live wrong effective client DNS, IP control, hostname failure and restoredHTTPS verified |
| F18 | Explicit leaf paths and approved CA / client trust | Team faculty confirmation and all-four-client trust verified |
| F19 | Full-system viva notes / actual HTTP2 | HTTP2 negotiated; viva remains live |
| F20 | Eleven-step integrated runbook | Procedures complete; faculty challenge remains live |
| F21 | Weak/list/wildcard validators via Werkzeug | Regression cases pass |
| F22 | Printable architecture layout corrected | Four-page PDF preserved with wrapped flow and diagrams |

Local source/config tests are distinct from a four-Mac network trial. No missing
packet capture, ping response or timed cutover result is generated as evidence.
