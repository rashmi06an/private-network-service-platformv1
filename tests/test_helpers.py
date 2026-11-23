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
if scenario=='missingetag':
 policy='public, max-age=60' if a[-1].endswith('/api/cache-demo') else 'no-store'
 headers=headers.replace('\\r\\n\\r\\n','\\r\\nCache-Control: '+policy+'\\r\\n\\r\\n')
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
     if scenario=='missingetag':self.assertIn('cache-demo returned no ETag',r.stdout+r.stderr)


 def test_mixed_old_and_new_backend_deployment_is_rejected(self):
  with tempfile.TemporaryDirectory() as d:
   curl=Path(d)/'curl'
   curl.write_text("""#!/usr/bin/env python3
import os,sys
from pathlib import Path
a=sys.argv[1:]; scenario=os.environ['CASE']; url=a[-1]
label='A' if ':3001/' in url else 'B'
cache=url.endswith('/api/cache-demo')
old=(scenario=='old-a' and label=='A') or (scenario=='old-b' and label=='B')
conditional='-H' in a
code='304' if cache and conditional and not old else '200'
headers=['HTTP/1.1 '+code+' Test','X-Backend: '+label]
if cache:
 headers += ['Cache-Control: public, max-age=60', 'ETag: '+ ('"backend-'+label.lower()+'-v1"' if old else '"team1-cache-v2"')]
else:
 if not old: headers += ['Cache-Control: no-store']
if scenario=='old-validator-only' and cache and label=='B':
 headers=[h if not h.startswith('ETag:') else 'ETag: "backend-b-v1"' for h in headers]
if scenario=='broken-conditional' and cache and conditional and label=='B':
 code='200'; headers[0]='HTTP/1.1 200 Test'
Path(a[a.index('-D')+1]).write_text('\\r\\n'.join(headers)+'\\r\\n\\r\\n')
print(code,end='')
""")
   curl.chmod(0o755)
   for scenario,success in [('updated',True),('old-a',False),('old-b',False),
                            ('old-validator-only',False),('broken-conditional',False)]:
    with self.subTest(scenario=scenario):
     env=dict(os.environ,TEAM_CURL=str(curl),CASE=scenario)
     r=subprocess.run(['bash',str(ROOT/'scripts/test-backends.sh')],env=env,text=True,capture_output=True)
     if success:self.assertEqual(r.returncode,0,r.stdout+r.stderr)
     else:
      self.assertNotEqual(r.returncode,0,r.stdout+r.stderr)
      self.assertIn('FAIL:',r.stdout+r.stderr)

if __name__=='__main__':unittest.main()
