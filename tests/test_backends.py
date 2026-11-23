"""Offline tests: python3 -m unittest discover -s tests -v."""
from pathlib import Path
import importlib.util
import unittest

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

if __name__=='__main__':unittest.main()
