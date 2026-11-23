"""Isolated PF command fixtures verify original enable state and unrelated owners."""
from pathlib import Path
import os
import shutil
import subprocess
import tempfile
import unittest

ROOT=Path(__file__).resolve().parents[1]
class PFRollback(unittest.TestCase):
 def test_restore_pre_enabled_pf_without_disabling_other_owners(self):
  for before,released,expected,needs_enable in [('Enabled','Disabled','Enabled',True),('Disabled','Disabled','Disabled',False),('Disabled','Enabled','Enabled',False),('Enabled','Enabled','Enabled',False)]:
   with self.subTest(before=before,released=released),tempfile.TemporaryDirectory() as directory:
    root=Path(directory);(root/'scripts').mkdir();binary=root/'bin';binary.mkdir()
    for name in ['lib.sh','firewall-isolation.sh']:shutil.copy2(ROOT/'scripts'/name,root/'scripts'/name)
    state=root/'.local-state/pf-isolation';state.mkdir(parents=True)
    (state/'active-token').write_text('123\n')
    (state/'info-before.txt').write_text('Status: '+before+' for 1 days\n')
    (state/'main-before.txt').write_text('anchor "com.apple/*" all\n')
    current=root/'status';current.write_text('Enabled')
    log=root/'calls'
    (binary/'sudo').write_text('#!/bin/sh\nexec "$@"\n')
    (binary/'ipconfig').write_text('#!/bin/sh\necho 10.7.27.247\n')
    (binary/'pfctl').write_text('''#!/usr/bin/env python3
from pathlib import Path
import json,os,sys
a=sys.argv[1:]
with open(os.environ['PF_CALL_LOG'],'a') as output:output.write(json.dumps(a)+'\\n')
p=Path(os.environ['PF_CURRENT'])
if a==['-X','123']:p.write_text(os.environ['PF_RELEASED'])
elif a==['-e']:p.write_text('Enabled')
elif a==['-s','info']:print('Status: '+p.read_text()+' for 0 days')
elif a==['-sr']:print('anchor "com.apple/*" all')
elif a in [['-a','com.apple/team1_submission','-F','rules'],['-a','com.apple/team1_submission','-vvsr']]:pass
else:raise SystemExit('Unexpected or unsafe PF command: '+str(a))
''')
    for file in binary.iterdir():file.chmod(0o755)
    env=dict(os.environ,PATH=str(binary)+':'+os.environ['PATH'],PF_CURRENT=str(current),PF_CALL_LOG=str(log),PF_RELEASED=released)
    result=subprocess.run(['bash',str(root/'scripts/firewall-isolation.sh'),'rollback'],env=env,text=True,capture_output=True)
    self.assertEqual(result.returncode,0,result.stdout+result.stderr)
    self.assertEqual(current.read_text(),expected)
    calls=log.read_text()
    self.assertEqual('["-e"]' in calls,needs_enable)
    self.assertNotIn('["-d"]',calls)
    self.assertFalse((state/'active-token').exists())
    self.assertTrue(list(state.glob('released-token-*')))
    self.assertEqual((state/'main-before.txt').read_bytes(),(state/'main-after.txt').read_bytes())

if __name__=='__main__':unittest.main()
