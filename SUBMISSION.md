# Submission - Team Scout Regiment

**Private Network Service Platform · Computer Networks · 23 November 2026**

Submission branch: `samiksha/submission-readiness`.
This package contains the corrected source/configuration, both reports, architecture
PDF, original screenshots from main, new timestamped verification and viva/runbook.
Further team-side collection was ended at the team's request.

## Open these first

1. [Architecture PDF](docs/architecture-document.pdf) and [current inventory](docs/network-inventory.md).
2. [Phase1 report](reports/phase1-report.md) and [Phase2 results + six learning summaries](reports/phase2-report.md).
3. [Screenshot gallery](docs/submission-evidence.html) - original images grouped by topic, with limitations labelled.
4. [Evidence ledger](reports/verification-status.json), [packet index](evidence/verification/packet-index.md) and [historical failures](evidence/failures/INDEX.md).
5. [Final validation](reports/final-validation.json), [11-step demonstration](docs/phase2-demo-runbook.md) and [viva notes](docs/viva-notes.md).

Follow-up: ping acceptance is now verified after the three repaired incoming
directions. Collection resumed at team request; the earlier ZIP remains its dated
snapshot until the remaining follow-up evidence is finalized.

Saved packet capture and live wrong-client-DNS/recovery are now verified too.
The current ledger has12 verified items; only full timed cutover remains open.

## Verified results

Both current backends, trusted HTTPS, A/B balancing, shared cache validator/304 and
HTTP2 are verified. Both private resolvers are configured on all four clients.
Controlled primary-DNS failure, natural TTL expiry, separate manual flush, scoped
backend isolation/rollback, and A-down/B-only/recovery have reviewed live evidence.
The team confirmed faculty approval for the existing mkcert method; all four
clients trust both the original primary and separate same-CA standby certificate.

## Disclosed evidence limits

- Standby A/B/trust, fresh-new routing and restoration are observed. The first
  cached-old cutover run failed; a later cache preflight passes, but the complete
  concurrent cached-old/fresh-new/convergence retry was not supplied.


The source/package checks can pass while the strict live-evidence gate remains
nonzero for the remaining cutover item. Faculty-injected diagnosis and individual viva remain
live assessment tasks. This package does not certify unperformed experiments.

## Source checks

```bash
python3 -m venv .venv
. .venv/bin/activate
python -m pip install -r backend-a/requirements.txt
python -m unittest discover -s tests -v
python scripts/submission-check.py --source-only
```

The strict `python scripts/submission-check.py` additionally requires every reviewed
live-evidence item. No private keys, local service PIDs, PF tokens, virtual
environments or `.git` directory belong in the submission archive.
