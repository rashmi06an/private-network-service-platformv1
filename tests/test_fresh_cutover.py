"""Scheduled fresh-client proof must reject wrong routes and late results."""
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest
ROOT=Path(__file__).resolve().parents[1]
class FreshCutover(unittest.TestCase):
 def test_route_identity_and_timing(self):
  with tempfile.TemporaryDirectory() as directory:
   root=Path(directory);(root/'scripts').mkdir();binary=root/'bin';binary.mkdir()
   shutil.copy2(ROOT/'scripts/lib.sh',root/'scripts/lib.sh')
   curl=binary/'curl'
   script=root/'scripts/fresh-cutover-client.sh'
   script.write_text((ROOT/'scripts/fresh-cutover-client.sh').read_text().replace('/usr/bin/curl',str(curl)))
   commands={
    'ipconfig':'#!/bin/sh\necho "${TEST_IP:-10.7.27.145}"\n',
    'date':'''#!/usr/bin/env python3
from pathlib import Path
import os,sys
if sys.argv[1:]==['+%s']:
 p=Path(os.environ['DATE_COUNT']);n=int(p.read_text())+1 if p.exists() else 1;p.write_text(str(n))
 offset=11 if os.environ['CASE']=='missed' else (26 if os.environ['CASE']=='late-result' and n>=3 else 5)
 print(1000000000+offset)
else:print('fixture-UTC')
''',
    'sudo':'#!/bin/sh\nif [ "$1" = -v ]; then exit 0; fi\nexec "$@"\n',
    'dscacheutil':'#!/bin/sh\nif [ "$1" = -q ]; then printf "name: app.team1.test\\nip_address: 10.7.28.78\\n"; fi\n',
    'killall':'#!/bin/sh\nexit 0\n',
    'curl':'''#!/usr/bin/env python3
from pathlib import Path
import os,sys
a=sys.argv[1:]
edge='primary-mac2' if os.environ['CASE']=='wrong-edge' else 'standby-mac3'
Path(a[a.index('-D')+1]).write_text('HTTP/2 200\\r\\nX-Edge: '+edge+'\\r\\n\\r\\n')
print('200 '+('10.7.25.25' if os.environ['CASE']=='wrong-ip' else '10.7.28.78'),end='')
'''}
   for name,text in commands.items():
    p=binary/name;p.write_text(text);p.chmod(0o755)
   for scenario,ip,success in [('correct','10.7.27.145',True),('wrong-ip','10.7.27.145',False),('wrong-edge','10.7.27.145',False),('late-result','10.7.27.145',False),('missed','10.7.27.145',False),('correct','10.7.27.247',False)]:
    with self.subTest(scenario=scenario,ip=ip):
     count=root/'date-count';count.unlink(missing_ok=True)
     env=dict(os.environ,PATH=str(binary)+':'+os.environ['PATH'],CASE=scenario,TEST_IP=ip,DATE_COUNT=str(count))
     result=subprocess.run(['bash',str(script),'1000000000'],env=env,text=True,capture_output=True)
     self.assertEqual(result.returncode==0,success,result.stdout+result.stderr)
     if not success:self.assertIn('FAIL:',result.stdout+result.stderr)
if __name__=='__main__':unittest.main()
