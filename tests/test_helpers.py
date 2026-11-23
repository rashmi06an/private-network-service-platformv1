"""Negative scenarios must fail even when curl/dig themselves exit zero."""
from pathlib import Path
import os
import subprocess
import tempfile
import unittest
ROOT=Path(__file__).resolve().parents[1]
class Helpers(unittest.TestCase):
 def test_wrong_http_dns_or_identity_does_not_pass(self):
  with tempfile.TemporaryDirectory() as d:
   folder=Path(d)
   (folder/'curl').write_text('''#!/usr/bin/env python3
import os,sys
from pathlib import Path
a=sys.argv[1:]; scenario=os.environ['CASE']
code='502' if scenario=='ha502' else '200'
headers='HTTP/1.1 '+code+' Test\\r\\nX-Backend: B\\r\\nX-Edge: primary-mac2\\r\\n\\r\\n'
if '-D' in a:Path(a[a.index('-D')+1]).write_text(headers)
print(code,end='')
''')
   (folder/'dig').write_text('#!/bin/bash\necho ";; status: NXDOMAIN, ANSWER: 0"\nexit 0\n')
   (folder/'ipconfig').write_text('#!/bin/bash\necho 10.7.27.145\n')
   for file in folder.iterdir():file.chmod(0o755)
   env=dict(os.environ,PATH=d+':'+os.environ['PATH'],TEAM_CURL=str(folder/'curl'))
   for script,arguments,scenario in [
    ('test-ha-failover.sh',['a-down'],'ha502'),
    ('test-load-balancing.sh',[],'onlyb'),
    ('test-backend-isolation.sh',[],'openisolation'),
    ('test-backup-dns.sh',[],'nxdomain'),
    ('test-https.sh',[],'missingetag')]:
    with self.subTest(script=script):
     r=subprocess.run(['bash',str(ROOT/'scripts'/script),*arguments],env=dict(env,CASE=scenario),text=True,capture_output=True)
     self.assertNotEqual(r.returncode,0,r.stdout+r.stderr)
     self.assertIn('FAIL:',r.stdout+r.stderr)

if __name__=='__main__':unittest.main()
