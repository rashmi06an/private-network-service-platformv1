"""A non-answering temporary cache must never replace the system resolver."""
import importlib.util
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[1]

class CachePreflight(unittest.TestCase):
 def test_forwarding_is_required_before_any_system_resolver_change(self):
  for reachable in [False,True]:
   with self.subTest(reachable=reachable),tempfile.TemporaryDirectory() as directory:
    spec=importlib.util.spec_from_file_location('ttl_probe',ROOT/'scripts/ttl-experiment.py')
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    root=Path(directory);binary=root/'dnsmasq';binary.touch();commands=[];queries=[]
    def execute(args,**kwargs):
     commands.append(args)
     if args[:2]==['ipconfig','getifaddr']:return subprocess.CompletedProcess(args,0,'10.7.25.25','')
     for arg in args:
      if arg.startswith('--pid-file='):Path(arg.split('=',1)[1]).write_text('12345')
     return subprocess.CompletedProcess(args,0,'','')
    def subrun(args,**kwargs):
     if args[0]=='ps':
      return subprocess.CompletedProcess(args,0,str(next(root.rglob('client-cache.conf'))),'')
     return subprocess.CompletedProcess(args,0,'','')
    def expected(server,port,name,ip):
     queries.append(server)
     if server==module.OLD and not reachable:raise RuntimeError('cache does not answer')
     return ip,30
    with patch.object(module,'ROOT',root),patch.object(module.shutil,'which',return_value=str(binary)),patch.object(module.time,'time',return_value=1000000000),patch.object(module,'run',side_effect=execute),patch.object(module.subprocess,'run',side_effect=subrun),patch.object(module,'expected',side_effect=expected),patch.object(sys,'argv',['ttl-experiment.py','cutover','1000000060','--preflight']):
     if reachable:module.main()
     else:
      with self.assertRaisesRegex(RuntimeError,'cache does not answer'):module.main()
    self.assertEqual(queries,[module.PRIMARY,module.BACKUP,module.OLD])
    self.assertFalse(any('install' in cmd or 'dscacheutil' in cmd or 'mDNSResponder' in cmd for cmd in commands))
    self.assertTrue(any(cmd[:3]==['sudo','kill','-TERM'] for cmd in commands))
    self.assertTrue(any(any(arg.startswith('--user=') for arg in cmd) for cmd in commands))
if __name__=='__main__':unittest.main()
