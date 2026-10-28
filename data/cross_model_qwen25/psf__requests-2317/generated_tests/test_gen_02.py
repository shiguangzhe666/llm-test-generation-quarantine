import unittest
from unittest.mock import patch, Mock
from requests import Session, Request, Response, PreparedRequest
from requests.packages.urllib3.connectionpool import HTTPConnectionPool
from requests.cookies import cookiejar_from_dict
from requests.adapters import HTTPAdapter
from requests.utils import get_environ_proxies

class TestRequestsSession(unittest.TestCase):

    def setUp(self):
        self.session = Session()

    def test_get(self):
        response = Response()
        response.status_code = 200
        response._content = b'{"key": "value"}'
        prepared_request = PreparedRequest()
        prepared_request.prepare_url = Mock(return_value="http://test.com")
        with patch.object(HTTPConnectionPool, 'request', return_value=response) as mock_request:
            result = self.session.get("http://test.com")
            mock_request.assert_called_once_with('GET', 'http://test.com', **{})
            self.assertEqual(result.json(), {"key": "value"})

    def test_post(self):
        response = Response()
        response.status_code = 201
        response._content = b'{"key": "value"}'
        prepared_request = PreparedRequest()
        prepared_request.prepare_url = Mock(return_value="http://test.com")
        with patch.object(HTTPConnectionPool, 'request', return_value=response) as mock_request:
            result = self.session.post("http://test.com", data={"key": "value"})
            mock_request.assert_called_once_with('POST', 'http://test.com', data=b'{"key": "value"}', **{})
            self.assertEqual(result.json(), {"key": "value"})

    def test_close(self):
        self.session.close()
        self.assertTrue(all(adapter.closed for adapter in self.session.adapters.values()))

    def test_mount(self):
        adapter = HTTPAdapter()
        self.session.mount('http://', adapter)
        self.assertIn('http://', self.session.adapters)

    def test_merge_environment_settings(self):
        settings = self.session.merge_environment_settings('http://test.com', {}, True, True, None)
        self.assertEqual(settings['verify'], True)
        self.assertEqual(settings['proxies'], {})

    def test_get_adapter(self):
        adapter = HTTPAdapter()
        self.session.mount('http://', adapter)
        self.assertEqual(self.session.get_adapter('http://example.com'), adapter)

    def test_resolve_redirects(self):
        response = Response()
        response.status_code = 301
        response.headers['Location'] = 'http://test.com'
        response._content = b''
        request = Request('GET', 'http://test.com')
        prepped = request.prepare()
        session = Session()
        session.mount('http://', HTTPAdapter())
        with patch.object(session, 'send', return_value=response) as mock_send:
            result = session.resolve_redirects(response, prepped)
            mock_send.assert_called_once_with(response, allow_redirects=True)
            self.assertEqual(result.url, 'http://test.com')

    def test_session_context_manager(self):
        with session() as s:
            pass
        self.assertTrue(s.closed)

if __name__ == '__main__':
    unittest.main()