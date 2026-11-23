# Audit finding closure and live acceptance

Source corrections are distinct from four-Mac live verification. The latter is
tracked in [verification-status.json](../reports/verification-status.json).

| Audit ID | Correction | Remaining acceptance |
|---|---|---|
| F01 | Direct-server TTL countdown claim removed; real caching resolver and synchronized schedule added | record actual natural expiry |
| F02 | Separate manual-flush experiment; mandatory status retained | actual OLD→NEW before expiry |
| F03 | Shared hosts-data format, exact assertions, fresh failover procedure | migrate both services; synchronize and capture fresh failover |
| F04 | Both DNS operators scheduled; old/fresh/new and synchronized restore specified | execute cutover and restoration |
| F05 | Reachable com.apple anchor verified; narrow rules match helper | execute on both backends; counters/allowed/denied |
| F06 | Before-state backup and owned PF enable token; scoped rollback | save actual rollback/restored tests |
| F07 | C rollback boundary explicit; optional temporary two-edge policy | demonstrate intended policy/state |
| F08 | Single nginx location retains X-Edge everywhere | deploy and verify both edges |
| F09 | Shared cache representation/ETag and correct endpoint; 304 asserted | restart both updated apps and capture HTTPS304 |
| F10 | All shell helpers executable | fresh-clone invocation |
| F11 | Assertions fail on wrong codes/identities/DNS answers | negative local checks and real stage outputs |
| F12 | Capture commands and required saved-capture/packet-index gate | attach actual capture and frame guide |
| F13 | Controlled trusted TLS 1.2 capture plus TLS 1.3 explanation | attach Certificate packet exhibit |
| F14 | Completion claims reconciled; results tied to evidence ledger | finalize after actual evidence review |
| F15 | Historical index describes actual image contents; no filename-only pass | new transcripts/captures indexed after review |
| F16 | Four role-specific inventory/all-pairs ping checks | all four real logs |
| F17 | Early Phase 1 DNS lease explicitly historical | effective wrong-client-resolver demo if required literally |
| F18 | Explicit leaf filenames; publicCA-only trust; standby leaf distinction | confirm faculty CA approval and all-client trust |
| F19 | Full-system notes including HTTP/2/3, TCP flow control, email/cache | actual HTTP/2 exhibit and personal viva |
| F20 | Current 11-step role/firewall-aware runbook | full-team rehearsal and live challenge |
| F21 | Werkzeug handles weak/list/wildcard cache validators | offline regression checks |
| F22 | Print flow wraps, heading/page layout corrected; PDF regenerated | visual PDF inspection |

An item's implementation correction is not a claim that its live requirement has
already passed. Keep original failed experiments labeled as diagnostic/historical.
