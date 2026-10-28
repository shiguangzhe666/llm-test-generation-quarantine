import unittest
import requests

class TestSession(unittest.TestCase):
    
    def setUp(self):
        self.session = requests.Session()
        self.session.mount('http://', requests.adapters.HTTPAdapter(max_retries=3))
        self.session.mount('https://', requests.adapters.HTTPAdapter(max_retries=3))

    def test_get(self):
        r = self.session.get('https://httpbin.org/get')
        self.assertEqual(r.status_code, 200)

    def test_post(self):
        r = self.session.post('https://httpbin.org/post', data = {'key': 'value'})
        self.assertEqual(r.status_code, 200)

    def test_put(self):
        r = self.session.put('https://httpbin.org/put', data = {'key': 'value'})
        self.assertEqual(r.status_code, 200)

    def test_delete(self):
        r = self.session.delete('https://httpbin.org/delete')
        self.assertEqual(r.status_code, 200)

    def test_patch(self):
        r = self.session.patch('https://httpbin.org/patch', data = {'key': 'value'})
        self.assertEqual(r.status_code, 200)

    def test_options(self):
        r = self.session.options('https://httpbin.org/get')
        self.assertEqual(r.status_code, 200)

    def test_head(self):
        r = self.session.head('https://httpbin.org/get')
        self.assertEqual(r.status_code, 200)

    def test_cookies(self):
        r = self.session.get('https://httpbin.org/cookies', cookies={'from-my':'cookie'})
        self.assertEqual(r.status_code, 200)

    def test_timeout(self):
        with self.assertRaises(requests.Timeout):
            self.session.get('https://httpbin.org/get', timeout=0.01)

    def test_redirects(self):
        r = self.session.get('https://httpbin.org/redirect/1', allow_redirects=False)
        self.assertEqual(r.status_code, 302)

    def test_stream(self):
        r = self.session.get('https://httpbin.org/stream/1', stream=False)
        self.assertEqual(r.status_code, 200)

    def test_verify(self):
        r = self.session.get('https://httpbin.org/get', verify=False)
        self.assertEqual(r.status_code, 200)

    def test_cert(self):
        r = self.session.get('https://httpbin.org/get', cert=('path/client.crt', 'path/client.key'))
        self.assertEqual(r.status_code, 200)

    def test_proxies(self):
        r = self.session.get('https://httpbin.org/get', proxies={'https': 'https://10.10.1.10:1080'})
        self.assertEqual(r.status_code, 200)

    def tearDown(self):
        self.session.close()

if __name__ == '__main__':
    unittest.main()