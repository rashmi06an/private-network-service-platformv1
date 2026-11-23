"""Exercise resolver rollback and failure classification with isolated OS fixtures."""
from pathlib import Path
import os
import shutil
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]

class WrongDNS(unittest.TestCase):
    def test_effective_fault_rollback_and_unrelated_failures(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root/'scripts').mkdir()
            binary = root/'bin'; binary.mkdir()
            target = root/'resolver'
            original = 'nameserver 10.7.27.145\nnameserver 10.7.27.247\n'
            for name in ['lib.sh', 'test-https.sh', 'wrong-client-dns-demo.sh']:
                copied = root/'scripts'/name
                shutil.copy2(ROOT/'scripts'/name, copied)
                if name == 'wrong-client-dns-demo.sh':
                    copied.write_text(copied.read_text().replace('target=/etc/resolver/team1.test', 'target='+str(target)))
            programs = {
                'ipconfig': '#!/bin/sh\necho 10.7.25.25\n',
                'lsof': '#!/bin/sh\nif [ "$CASE" = busy ]; then echo "Owned-by-another-DNS-process"; exit 0; fi\nexit 1\n',
                'ping': '#!/bin/sh\necho "IP reachable"\n',
                'scutil': '#!/bin/sh\necho "domain : team1.test"\n',
                'dscacheutil': '#!/bin/sh\nexit 0\n',
                'killall': '#!/bin/sh\nexit 0\n',
                'sudo': '''#!/usr/bin/env python3
import os,sys
a=sys.argv[1:]
if a==['-v']:sys.exit(0)
if os.environ['CASE']=='install-fails' and a[0]=='install':sys.exit(1)
allowed={'lsof','cp','install','rm','dscacheutil','killall'}
if a[0] not in allowed:raise SystemExit('Unexpected fixture command: '+a[0])
os.execvp(a[0],a)
''',
                'curl': '''#!/usr/bin/env python3
import os,sys
from pathlib import Path
a=sys.argv[1:]
bad=Path(os.environ['TEST_RESOLVER']).read_text().startswith('nameserver 10.7.25.25\\n')
if bad:
 if os.environ['CASE']=='dns-timeout':
  print('curl: (28) Resolving timed out after 3000 milliseconds',file=sys.stderr);sys.exit(28)
 if os.environ['CASE']=='tls-error':
  print('SSL certificate problem',file=sys.stderr);sys.exit(60)
 print('curl: (6) Could not resolve host: app.team1.test',file=sys.stderr);sys.exit(6)
cache=a[-1].endswith('/api/cache-demo')
code='304' if cache and '-H' in a else '200'
headers=['HTTP/2 '+code,'X-Backend: A','X-Edge: primary-mac2']
headers += ['Cache-Control: public, max-age=60','ETag: "team1-cache-v2"'] if cache else ['Cache-Control: no-store']
if '-D' in a:Path(a[a.index('-D')+1]).write_text('\\r\\n'.join(headers)+'\\r\\n\\r\\n')
print(code,end='')
'''
            }
            for name,text in programs.items():
                path=binary/name;path.write_text(text);path.chmod(0o755)
            for scenario,success in [('dns-error', True), ('dns-timeout', True), ('tls-error', False), ('busy', False), ('install-fails', False)]:
                with self.subTest(scenario=scenario):
                    target.write_text(original)
                    env=dict(os.environ,PATH=str(binary)+':'+os.environ['PATH'],TEAM_CURL=str(binary/'curl'),TEST_RESOLVER=str(target),CASE=scenario)
                    run=subprocess.run(['bash',str(root/'scripts/wrong-client-dns-demo.sh')],env=env,text=True,capture_output=True)
                    self.assertEqual(run.returncode==0,success,run.stdout+run.stderr)
                    self.assertEqual(target.read_text(), original)
                    if scenario=='tls-error':self.assertIn('not a DNS-resolution error',run.stdout+run.stderr)
                    if scenario=='busy':self.assertIn('already has a port53 socket',run.stdout+run.stderr)

if __name__=='__main__':unittest.main()
