import os
import time
import requests
import unittest
from requests.adapters import HTTPAdapter
from requests.models import PreparedRequest, Response
from requests.packages.urllib3.poolmanager import PoolManager

class TestSession(unittest.TestCase):
    def setUp(self):
        self.session = session()
        self.url = 'https://httpbin.org/get'

    def tearDown(self):
        self.session.close()

    def test_get_request(self):
        response = self.session.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTrue('args' in response.json())

    def test_post_request(self):
        data = {'key': 'value'}
        response = self.session.post(self.url, data=data)
        self.assertEqual(response.status_code, 200)
        self.assertTrue('form' in response.json() and response.json()['form'] == data)

    def test_custom_adapter(self):
        class MyAdapter(HTTPAdapter):
            def build_response(self, req, **kwargs):
                return Response(req, 200, 'OK', None, None, [b''])

        self.session.mount('http://', MyAdapter())
        response = self.session.get('http://httpbin.org/get')
        self.assertEqual(response.status_code, 200)

    def test_timeout(self):
        start_time = time.time()
        try:
            self.session.get(self.url, timeout=0.01)
        except requests.exceptions.Timeout:
            pass
        else:
            self.fail("Timeout exception not raised")
        self.assertGreater(time.time() - start_time, 0.01)

    def test_proxies(self):
        proxies = {'http': 'http://127.0.0.1:8888', 'https': 'https://127.0.0.1:8888'}
        response = self.session.get(self.url, proxies=proxies)
        self.assertEqual(response.status_code, 200)

    def test_cookies(self):
        self.session.cookies.set('test_cookie', 'test_value')
        response = self.session.get(self.url)
        self.assertEqual(response.cookies.get_dict(), {'test_cookie': 'test_value'})

    def test_hooks(self):
        def response_hook(r, *args, **kwargs):
            self.assertEqual(r.status_code, 200)
            return r

        self.session.hooks = {'response': [response_hook]}
        response = self.session.get(self.url)
        self.assertEqual(response.status_code, 200)

if __name__ == '__main__':
    unittest.main()