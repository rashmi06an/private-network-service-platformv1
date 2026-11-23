"""Real detached-process lifecycle on an isolated loopback port; no lab services touched."""
import json
import os
from pathlib import Path
import shutil
import socket
import subprocess
import sys
import tempfile
import unittest

ROOT=Path(__file__).resolve().parents[1]

class BackendService(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory(prefix='backend manager test ')
        self.root=Path(self.temp.name)
        (self.root/'scripts').mkdir();(self.root/'bin').mkdir()
        with socket.socket() as reserve:
            reserve.bind(('127.0.0.1',0));self.port=reserve.getsockname()[1]
        source=(ROOT/'scripts/backend-service.py').read_text()
        expected="'b': ('10.7.27.247', 3002)"
        self.assertIn(expected,source)
        self.manager=self.root/'scripts/backend-service.py'
        self.manager.write_text(source.replace(expected,"'b': ('10.7.27.247', %s)" % self.port))
        ipconfig=self.root/'bin/ipconfig';ipconfig.write_text('#!/bin/sh\necho "${TEST_BACKEND_IP:-10.7.27.247}"\n');ipconfig.chmod(0o755)
        backend=self.root/'backend-b';(backend/'.venv/bin').mkdir(parents=True)
        (backend/'.venv/bin/python').symlink_to(sys.executable)
        (backend/'app.py').write_text('''from http.server import BaseHTTPRequestHandler,HTTPServer
import json
class Handler(BaseHTTPRequestHandler):
 def do_GET(self):
  cache=self.path=='/api/cache-demo'
  data=json.dumps({'version':2} if cache else {'backend':'B','status':'ok'}).encode()
  self.send_response(200)
  self.send_header('Cache-Control','public, max-age=60' if cache else 'no-store')
  if cache:self.send_header('ETag','"team1-cache-v2"')
  self.send_header('Content-Length',str(len(data)));self.end_headers();self.wfile.write(data)
HTTPServer(('127.0.0.1',%s),Handler).serve_forever()
''' % self.port)
        self.env=dict(os.environ,PATH=str(self.root/'bin')+':'+os.environ['PATH'])
        self.state=self.root/'.local-state/backend-services/b.json'
        self.addCleanup(self.cleanup)
    def call(self,action,env=None):
        return subprocess.run([sys.executable,str(self.manager),'b',action],env=env or self.env,text=True,capture_output=True,timeout=15)
    def cleanup(self):
        self.call('stop');self.temp.cleanup()
    def test_background_lifecycle_and_idempotence(self):
        first=self.call('start');self.assertEqual(first.returncode,0,first.stdout+first.stderr)
        pid=json.loads(self.state.read_text())['pid']
        os.kill(pid,0)
        again=self.call('start');self.assertEqual(again.returncode,0,again.stdout+again.stderr)
        self.assertEqual(json.loads(self.state.read_text())['pid'],pid)
        status=self.call('status');self.assertEqual(status.returncode,0,status.stdout+status.stderr)
        stopped=self.call('stop');self.assertEqual(stopped.returncode,0,stopped.stdout+stopped.stderr)
        self.assertFalse(self.state.exists());self.assertNotEqual(self.call('status').returncode,0)
        self.assertEqual(self.call('start').returncode,0)
    def test_wrong_machine_and_unregistered_port_are_refused(self):
        wrong=self.call('start',dict(self.env,TEST_BACKEND_IP='10.7.25.25'))
        self.assertNotEqual(wrong.returncode,0);self.assertIn('Wrong Mac',wrong.stderr)
        with socket.socket() as foreign:
            foreign.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
            foreign.bind(('127.0.0.1',self.port));foreign.listen()
            busy=self.call('start');self.assertNotEqual(busy.returncode,0)
            self.assertIn('already occupied',busy.stderr)
            self.assertEqual(foreign.getsockname()[1],self.port)
        self.assertFalse(self.state.exists())
    def test_foreign_process_registration_is_never_signalled(self):
        foreign=subprocess.Popen([sys.executable,'-c','import time;time.sleep(30)'],start_new_session=True)
        try:
            self.state.parent.mkdir(parents=True)
            birth=subprocess.check_output(['ps','-ww','-p',str(foreign.pid),'-o','lstart='],env=dict(os.environ,LC_ALL='C'),text=True).strip()
            self.state.write_text(json.dumps({'pid':foreign.pid,'uid':os.getuid(),'birth':birth}))
            result=self.call('stop');self.assertNotEqual(result.returncode,0)
            self.assertIn('refusing to signal',result.stderr)
            self.assertIsNone(foreign.poll())
        finally:
            foreign.terminate();foreign.wait(timeout=3)
            self.state.unlink(missing_ok=True)

if __name__=='__main__':unittest.main()
