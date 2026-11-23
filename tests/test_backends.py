"""Offline tests: python3 -m unittest discover -s tests -v."""
from pathlib import Path
import importlib.util
import unittest
import threading
import urllib.error
import urllib.request
from werkzeug.serving import make_server

ROOT=Path(__file__).resolve().parents[1]
def load(label):
    spec=importlib.util.spec_from_file_location('backend_'+label,ROOT/f'backend-{label.lower()}/app.py')
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    return module.app

class Backends(unittest.TestCase):
    def test_routes_and_status_are_not_cached(self):
        for label in 'AB':
            with self.subTest(backend=label),load(label).test_client() as c:
                for path in ['/', '/api/status']:
                    r=c.get(path);self.assertEqual(r.status_code,200)
                    self.assertEqual(r.json['backend'],label);self.assertEqual(r.headers['X-Backend'],label)
                self.assertEqual(c.get('/api/status').headers['Cache-Control'],'no-store')

    def test_cache_is_identical_and_validates_across_backends(self):
        a=load('A').test_client();b=load('B').test_client()
        r=a.get('/api/cache-demo');other=b.get('/api/cache-demo')
        self.assertEqual(r.data,other.data);self.assertEqual(r.headers['ETag'],other.headers['ETag'])
        self.assertEqual(r.headers['Cache-Control'],'public, max-age=60')
        self.assertEqual(other.headers['X-Backend'],'B')
        for value in [r.headers['ETag'],'W/'+r.headers['ETag'],'"other", '+r.headers['ETag'],'*']:
            with self.subTest(validator=value):
                checked=b.get('/api/cache-demo',headers={'If-None-Match':value})
                self.assertEqual(checked.status_code,304);self.assertEqual(checked.data,b'')
                self.assertEqual(checked.headers['ETag'],r.headers['ETag'])
        self.assertEqual(b.get('/api/cache-demo',headers={'If-None-Match':'"different"'}).status_code,200)
        self.assertEqual(b.head('/api/cache-demo').data,b'')


    def test_wire_cache_responses_have_one_date_header(self):
        opener=urllib.request.build_opener(urllib.request.ProxyHandler({}))
        for label in 'AB':
            server=make_server('127.0.0.1',0,load(label))
            thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
            try:
                url='http://127.0.0.1:%s/api/cache-demo' % server.server_port
                with opener.open(url,timeout=2) as response:
                    self.assertEqual(len(response.headers.get_all('Date')),1)
                    tag=response.headers['ETag']
                request=urllib.request.Request(url,headers={'If-None-Match':tag})
                try:
                    opener.open(request,timeout=2)
                    self.fail('Expected conditional304')
                except urllib.error.HTTPError as response:
                    self.assertEqual(response.code,304)
                    self.assertEqual(len(response.headers.get_all('Date')),1)
                    response.close()
            finally:
                server.shutdown();server.server_close();thread.join(timeout=2)

if __name__=='__main__':unittest.main()
