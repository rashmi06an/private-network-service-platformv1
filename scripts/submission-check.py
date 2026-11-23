#!/usr/bin/env python3
"""File/ledger gate, not a substitute for reviewing real network evidence."""
from pathlib import Path
import argparse
import json
import os
import re
import subprocess
import sys
ROOT=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser();p.add_argument('--source-only',action='store_true');args=p.parse_args()
errors=[]
required=['README.md','backend-a/app.py','backend-b/app.py','dns/project.hosts',
          'dns/dnsmasq.conf.example','dns/dnsmasq-phase2.conf.example','dns/backup-dnsmasq.conf.example',
          'edge/nginx.conf.example','edge/nginx-phase2.conf.example','edge/standby-nginx.conf.example',
          'edge/tls.conf.example','edge/tls-setup-notes.md','docs/architecture.md','docs/architecture-document.pdf',
          'docs/network-inventory.md','docs/team-commands.md','docs/phase2-demo-runbook.md',
          'docs/ttl-experiments.md','docs/packet-evidence.md','docs/viva-notes.md',
          'firewall/README.md','reports/phase1-report.md','reports/phase2-report.md','reports/verification-status.json']
for name in required:
 if not (ROOT/name).is_file():errors.append('Missing source/document: '+name)
for script in (ROOT/'scripts').glob('*.sh'):
 if not os.access(script,os.X_OK):errors.append('Not executable: '+script.name)
 if subprocess.run(['bash','-n',str(script)],capture_output=True).returncode:errors.append('Shell syntax: '+script.name)
for file in ROOT.rglob('*.md'):
 if any(part in ['.git','.venv','venv','.local-state'] for part in file.parts):continue
 for dest in re.findall(r'!?\[[^\]]*\]\(([^)]+)\)',file.read_text()):
  if '://' in dest or dest.startswith('#'):continue
  dest=dest.split('#')[0]
  if dest and not (file.parent/dest).exists():errors.append('Broken local link: '+str(file.relative_to(ROOT))+' -> '+dest)
ledger=json.loads((ROOT/'reports/verification-status.json').read_text())
pending=[]
for item in ledger['items']:
 if item['status']!='verified':pending.append(item['id']);continue
 if not item.get('review_note') or not item.get('artifacts'):errors.append('Verified item lacks reviewed artifacts/note: '+item['id'])
 for file in item.get('artifacts',[]):
  path=(ROOT/file).resolve()
  if not path.is_relative_to(ROOT) or not path.is_file() or path.stat().st_size==0:errors.append('Invalid/empty evidence path: '+file)
 if item['id']=='packet-capture' and not any(Path(f).suffix in ['.pcap','.pcapng'] for f in item.get('artifacts',[])):errors.append('Packet item needs an actual pcap/pcapng')
for error in errors:print('FAIL:',error)
print('Pending pre-evaluation evidence:',', '.join(pending) or 'none')
print('Live evaluation:',', '.join(x['id']+': '+x['status'] for x in ledger['live_evaluation']))
if errors:sys.exit(1)
if pending and not args.source_only:
 print('NOT READY: source checks passed, but mandatory reviewed live evidence is pending.');sys.exit(1)
print('PASS: source package checks' if args.source_only else 'PASS: source and pre-evaluation artifact ledger; challenge/viva remain live')
