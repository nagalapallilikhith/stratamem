import json
from pathlib import Path
import sys
import tempfile
import threading
import unittest
import urllib.request
import urllib.error
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import app

class HttpTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        app.DATA=Path(self.tmp.name)
        app.initialize()
        self.server=app.ThreadingHTTPServer(('127.0.0.1',0),app.Handler)
        self.thread=threading.Thread(target=self.server.serve_forever,daemon=True)
        self.thread.start()
        self.url='http://127.0.0.1:'+str(self.server.server_port)
    def tearDown(self):
        self.server.shutdown(); self.server.server_close(); self.thread.join()
        self.tmp.cleanup()
    def request(self,path,body=None,origin=None):
        headers={'Content-Type':'application/json'}
        if origin:headers['Origin']=origin
        req=urllib.request.Request(self.url+path,json.dumps(body).encode() if body is not None else None,headers)
        return urllib.request.urlopen(req)
    def test_http_workflow_and_private_files(self):
        with self.request('/api/state') as response:state=json.load(response)
        wid=state['workspace']['id']
        with self.request('/api/demo-step',{'workspace':wid,'step':0}) as response:self.assertIn('id',json.load(response))
        with self.request('/api/analyze',{'workspace':wid,'engine':'local'}) as response:self.assertEqual(json.load(response)['event_count'],1)
        for path in ['/data/connection.json','/app.py','/../README.md']:
            with self.assertRaises(urllib.error.HTTPError) as failure:self.request(path)
            self.assertEqual(failure.exception.code,404)
    def test_cross_origin_rejected(self):
        with self.assertRaises(urllib.error.HTTPError) as failure:self.request('/api/demo',{},'https://unrelated.example')
        self.assertEqual(failure.exception.code,403)
    def test_same_origin_and_safe_headers(self):
        with self.request('/api/demo',{},self.url) as response:self.assertIn('id',json.load(response))
        with self.request('/') as response:
            self.assertEqual(response.headers['X-Content-Type-Options'],'nosniff')
            self.assertIn("frame-ancestors 'none'",response.headers['Content-Security-Policy'])

if __name__=='__main__':unittest.main(verbosity=2)
