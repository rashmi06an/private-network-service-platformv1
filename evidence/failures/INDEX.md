# Reviewed historical failure exhibits

All linked PNGs are original main-branch evidence and remain byte-for-byte unchanged.
Historical addresses belong to Phase1; current source uses the Phase2 inventory.

| Failure | Evidence and interpretation |
|---|---|
| Wrong project DNS record | [Wrong record](wrong-dns-record.png): private DNS returns10.7.7.250; normal hostname curl resolves that IP then times out with28. [Record restored](wrong-dns-record-restored.png). |
| One backend unavailable | [Historical A-down](backend-a-down.png). Current controlled B-only200 and recoveredA/B are independently recorded in [the HA timeline](../verification/2026-11-23-ha-repair-and-recovery.json). |
| Both backends unavailable | [Both-down502](both-down-502.png): trusted hostname reaches nginx and receives HTTP502, following earlier B-only responses. [Recovery](recovery-after-restart.png). The image does not display both process-stop commands. |
| Wrong port | [Wrong port](wrong-port.png): ping10.7.21.15 receives2/2 replies, but port9999 curl fails with7. The host and port are independent identifiers. |
| Public resolver cannot answer private zone | [Public DNS](wrong-dns-server.png): explicit8.8.8.8 query fails; this does not show a changed effective client resolver. |
| DNS outage and restoration | [Unavailable](dns-unavailable.png), [restored](dns-unavailable-restored.png); current backup-DNS outage/recovery has separate timestamped logs. |

The live effective wrong-client-resolver demonstration was not completed before
the team ended collection. Its helper has local failure/rollback tests; those
fixtures are implementation validation, not a substitute for a live client exhibit.
