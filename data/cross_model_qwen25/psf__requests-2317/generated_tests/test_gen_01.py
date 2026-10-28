import requests
import unittest
from unittest.mock import patch, Mock

class TestSession(unittest.TestCase):

    def setUp(self):
        self.session = requests.Session()
        self.url = 'https://httpbin.org/get'

    def test_get_request(self):
        response = self.session.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_custom_header(self):
        headers = {'User-Agent': 'MyApp/1.0'}
        response = self.session.get(self.url, headers=headers)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers['User-Agent'], 'MyApp/1.0')

    def test_timeout(self):
        with patch('requests.Session.send') as mock_send:
            mock_send.return_value = Mock(status_code=200)
            response = self.session.get(self.url, timeout=0.001)
            self.assertEqual(response.status_code, 200)
            self.assertTrue(mock_send.call_args.kwargs['timeout'] <= 0.001)

    def test_proxies(self):
        proxies = {'http': 'http://10.10.1.10:3128', 'https': 'http://10.10.1.10:1080'}
        response = self.session.get(self.url, proxies=proxies)
        self.assertEqual(response.status_code, 200)

    def test_session_context_manager(self):
        with requests.Session() as session:
            response = session.get(self.url)
            self.assertEqual(response.status_code, 200)

if __name__ == '__main__':
    unittest.main()