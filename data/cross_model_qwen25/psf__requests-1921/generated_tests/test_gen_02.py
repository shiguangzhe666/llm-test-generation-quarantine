import unittest
from unittest.mock import patch, Mock
from requests.models import Response, PreparedRequest
from requests.exceptions import InvalidSchema
from requests.utils import get_environ_proxies
from requests.packages.urllib3.util.url import Url
from requests.packages.urllib3.connectionpool import HTTPConnectionPool

class TestSessionMethods(unittest.TestCase):

    def setUp(self):
        self.session = Session()

    def test_request(self):
        with patch('requests.sessions.Session.send') as mock_send:
            mock_response = Response()
            mock_response.status_code = 200
            mock_send.return_value = mock_response
            response = self.session.request('GET', 'http://example.com')
            self.assertEqual(response.status_code, 200)
            mock_send.assert_called_once()

    def test_get(self):
        with patch('requests.sessions.Session.send') as mock_send:
            mock_response = Response()
            mock_response.status_code = 200
            mock_send.return_value = mock_response
            response = self.session.get('http://example.com')
            self.assertEqual(response.status_code, 200)
            mock_send.assert_called_once()

    def test_post(self):
        with patch('requests.sessions.Session.send') as mock_send:
            mock_response = Response()
            mock_response.status_code = 201
            mock_send.return_value = mock_response
            response = self.session.post('http://example.com', data={'key': 'value'})
            self.assertEqual(response.status_code, 201)
            mock_send.assert_called_once()

    def test_options(self):
        with patch('requests.sessions.Session.send') as mock_send:
            mock_response = Response()
            mock_response.status_code = 200
            mock_send.return_value = mock_response
            response = self.session.options('http://example.com')
            self.assertEqual(response.status_code, 200)
            mock_send.assert_called_once()

    def test_head(self):
        with patch('requests.sessions.Session.send') as mock_send:
            mock_response = Response()
            mock_response.status_code = 200
            mock_send.return_value = mock_response
            response = self.session.head('http://example.com')
            self.assertEqual(response.status_code, 200)
            mock_send.assert_called_once()

    def test_put(self):
        with patch('requests.sessions.Session.send') as mock_send:
            mock_response = Response()
            mock_response.status_code = 200
            mock_send.return_value = mock_response
            response = self.session.put('http://example.com', data={'key': 'value'})
            self.assertEqual(response.status_code, 200)
            mock_send.assert_called_once()

    def test_patch(self):
        with patch('requests.sessions.Session.send') as mock_send:
            mock_response = Response()
            mock_response.status_code = 200
            mock_send.return_value = mock_response
            response = self.session.patch('http://example.com', data={'key': 'value'})
            self.assertEqual(response.status_code, 200)
            mock_send.assert_called_once()

    def test_delete(self):
        with patch('requests.sessions.Session.send') as mock_send:
            mock_response = Response()
            mock_response.status_code = 204
            mock_send.return_value = mock_response
            response = self.session.delete('http://example.com')
            self.assertEqual(response.status_code, 204)
            mock_send.assert_called_once()

    def test_mount_adapter(self):
        adapter = HTTPConnectionPool('http://example.com')
        self.session.mount('http://example.com', adapter)
        self.assertIn('http://example.com', self.session.adapters)

    def test_close(self):
        self.session.close()
        for adapter in self.session.adapters.values():
            self.assertTrue(adapter.closed)

    def test_invalid_schema(self):
        with self.assertRaises(InvalidSchema):
            self.session.get('ftp://example.com')

    def test_get_environ_proxies(self):
        with patch.dict('os.environ', {'http_proxy': 'http://proxy.example.com'}):
            proxies = get_environ_proxies('http://example.com')
            self.assertIn('http://proxy.example.com', proxies)

if __name__ == '__main__':
    unittest.main()