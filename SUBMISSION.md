# Submission - Team Scout Regiment

**Private Network Service Platform · Computer Networks · 23 November 2026**

Submission branch: `samiksha/submission-readiness`.
This package contains the corrected source/configuration, both reports, architecture
PDF, original screenshots from main, new timestamped verification and viva/runbook.
All13 pre-evaluation acceptance items are now verified, including the four
follow-up proofs. The strict source/evidence gate passes.

## Open these first

1. [Architecture PDF](docs/architecture-document.pdf) and [current inventory](docs/network-inventory.md).
2. [Phase1 report](reports/phase1-report.md) and [Phase2 results + six learning summaries](reports/phase2-report.md).
3. [Screenshot gallery](docs/submission-evidence.html) - original images grouped by topic, with limitations labelled.
4. [Evidence ledger](reports/verification-status.json), [packet index](evidence/verification/packet-index.md) and [historical failures](evidence/failures/INDEX.md).
5. [Final validation](reports/final-validation.json), [11-step demonstration](docs/phase2-demo-runbook.md) and [viva notes](docs/viva-notes.md).

## Verified results

Both current backends, trusted HTTPS, A/B balancing, shared cache validator/304 and
HTTP2 are verified. Both private resolvers are configured on all four clients.
Controlled primary-DNS failure, natural TTL expiry, separate manual flush, scoped
backend isolation/rollback, and A-down/B-only/recovery have reviewed live evidence.
The team confirmed faculty approval for the existing mkcert method; all four
clients trust both the original primary and separate same-CA standby certificate.

## Final evidence and restoration

- All12 directed ping paths have successful measured results across the baseline
  and repaired incoming-to-Mac1 follow-ups.
- Original57-packet capture and actual DNS/TCP/TLS/Certificate/ALPN frame index are included.
- Effective wrong-client DNS, normal lookup failure despite good IP reachability,
  and original-DNS/trusted HTTPS restoration are verified.
- Concurrent cached-old/fresh-new edge cutover and31.44second convergence are verified.
  Both DNS records and primary trusted HTTPS200/304 are restored and checked.

Source tests and isolated nginx checks pass; all61 original screenshots are preserved.
Detailed timelines retain prior failed attempts and their superseding successful runs.
Faculty-injected diagnosis and individual viva remain live assessment tasks. The
cutover is controlled manual DNS migration; it is not automatic edge failover.

## Source checks

```bash
python3 -m venv .venv
. .venv/bin/activate
python -m pip install -r backend-a/requirements.txt
python -m unittest discover -s tests -v
python scripts/submission-check.py --source-only
```

The strict `python scripts/submission-check.py` now passes with every reviewed
pre-evaluation evidence item. No private keys, local service PIDs, PF tokens, virtual
environments or `.git` directory belong in the submission archive.
