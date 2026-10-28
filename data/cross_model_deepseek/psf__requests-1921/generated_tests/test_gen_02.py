import unittest
import requests
from requests.exceptions import InvalidSchema

class TestSession(unittest.TestCase):
    
    def setUp(self):
        self.session = requests.Session()
        self.session.mount('http://', requests.adapters.HTTPAdapter(max_retries=3))
        self.session.mount('https://', requests.adapters.HTTPAdapter(max_retries=3))
    
    def test_get_adapter(self):
        self.assertRaises(InvalidSchema, self.session.get_adapter, 'ftp://example.com')
        self.assertIsInstance(self.session.get_adapter('http://example.com'), requests.adapters.HTTPAdapter)
        self.assertIsInstance(self.session.get_adapter('https://example.com'), requests.adapters.HTTPAdapter)
    
    def test_mount(self):
        self.session.mount('ftp://', requests.adapters.HTTPAdapter())
        self.assertIsInstance(self.session.get_adapter('ftp://example.com'), requests.adapters.HTTPAdapter)
    
    def test_get_request(self):
        response = self.session.get('http://httpbin.org/get')
        self.assertEqual(response.status_code, 200)
    
    def test_post_request(self):
        response = self.session.post('http://httpbin.org/post', data={'key': 'value'})
        self.assertEqual(response.status_code, 200)
    
    def test_redirect(self):
        response = self.session.get('http://httpbin.org/redirect/1', allow_redirects=False)
        self.assertEqual(response.status_code, 302)
        response = self.session.get('http://httpbin.org/redirect/1')
        self.assertEqual(response.status_code, 200)
    
    def tearDown(self):
        self.session.close()

if __name__ == '__main__':
    unittest.main()