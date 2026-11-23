# Current verification outputs

Use `scripts/record-evidence.sh` from the correct Mac to save actual command
output with host, UTC times, source commit and exit status. Preserve failures
as diagnostic runs rather than overwriting them with expected output.

The [acceptance ledger](../../reports/verification-status.json) links reviewed
artifacts. Local code-validation reports live in `reports/` and do not replace
four-Mac LAN, saved packet-capture, TTL, isolation or failover proof.

At submission, include the real saved protocol pcap/pcapng and a packet-index.md
using frame numbers from that capture. No private keys or PF enable tokens belong here.
