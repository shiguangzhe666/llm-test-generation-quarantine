import unittest
from unittest.mock import patch, Mock
from requests import Session, PreparedRequest, Response, RequestException
import requests.utils
import os

class TestSession(unittest.TestCase):
    def setUp(self):
        self.session = session()
        self.url = 'http://example.com'
        self.headers = {'Content-Type': 'application/json'}
        self.data = {'key': 'value'}

    def tearDown(self):
        self.session.close()

    def test_init(self):
        self.assertIsInstance(self.session, Session)

    def test_request(self):
        with patch('requests.Session.send', return_value=Mock(spec=Response)) as mock_send:
            self.session.request('GET', self.url, headers=self.headers, data=self.data)
            mock_send.assert_called_once_with(
                Request(method='GET', url=self.url, headers=self.headers, data=self.data),
                stream=False,
                timeout=None,
                allow_redirects=True,
                verify=True,
                cert=None,
                proxies={},
            )

    def test_get(self):
        with patch('requests.Session.send', return_value=Mock(spec=Response)) as mock_send:
            self.session.get(self.url, headers=self.headers, data=self.data)
            mock_send.assert_called_once_with(
                Request(method='GET', url=self.url, headers=self.headers, data=self.data),
                stream=False,
                timeout=None,
                allow_redirects=True,
                verify=True,
                cert=None,
                proxies={},
            )

    def test_post(self):
        with patch('requests.Session.send', return_value=Mock(spec=Response)) as mock_send:
            self.session.post(self.url, headers=self.headers, data=self.data)
            mock_send.assert_called_once_with(
                Request(method='POST', url=self.url, headers=self.headers, data=self.data),
                stream=False,
                timeout=None,
                allow_redirects=True,
                verify=True,
                cert=None,
                proxies={},
            )

    def test_options(self):
        with patch('requests.Session.send', return_value=Mock(spec=Response)) as mock_send:
            self.session.options(self.url, headers=self.headers, data=self.data)
            mock_send.assert_called_once_with(
                Request(method='OPTIONS', url=self.url, headers=self.headers, data=self.data),
                stream=False,
                timeout=None,
                allow_redirects=True,
                verify=True,
                cert=None,
                proxies={},
            )

    def test_head(self):
        with patch('requests.Session.send', return_value=Mock(spec=Response)) as mock_send:
            self.session.head(self.url, headers=self.headers, data=self.data)
            mock_send.assert_called_once_with(
                Request(method='HEAD', url=self.url, headers=self.headers, data=self.data),
                stream=False,
                timeout=None,
                allow_redirects=False,
                verify=True,
                cert=None,
                proxies={},
            )

    def test_put(self):
        with patch('requests.Session.send', return_value=Mock(spec=Response)) as mock_send:
            self.session.put(self.url, headers=self.headers, data=self.data)
            mock_send.assert_called_once_with(
                Request(method='PUT', url=self.url, headers=self.headers, data=self.data),
                stream=False,
                timeout=None,
                allow_redirects=True,
                verify=True,
                cert=None,
                proxies={},
            )

    def test_patch(self):
        with patch('requests.Session.send', return_value=Mock(spec=Response)) as mock_send:
            self.session.patch(self.url, headers=self.headers, data=self.data)
            mock_send.assert_called_once_with(
                Request(method='PATCH', url=self.url, headers=self.headers, data=self.data),
                stream=False,
                timeout=None,
                allow_redirects=True,
                verify=True,
                cert=None,
                proxies={},
            )

    def test_delete(self):
        with patch('requests.Session.send', return_value=Mock(spec=Response)) as mock_send:
            self.session.delete(self.url, headers=self.headers, data=self.data)
            mock_send.assert_called_once_with(
                Request(method='DELETE', url=self.url, headers=self.headers, data=self.data),
                stream=False,
                timeout=None,
                allow_redirects=True,
                verify=True,
                cert=None,
                proxies={},
            )

    def test_close(self):
        self.session.close()
        self.assertIsNone(self.session.cookies)

    def test_session_cookies(self):
        self.session.cookies = requests.utils.cookiejar_from_dict({'key': 'value'})
        self.assertEqual(self.session.cookies.get_dict(), {'key': 'value'})

    def test_send(self):
        with patch('requests.Session.send', return_value=Mock(spec=Response)) as mock_send:
            response = self.session.send(Mock(spec=PreparedRequest))
            mock_send.assert_called_once()

    def test_mount(self):
        adapter = Mock()
        self.session.mount('http://', adapter)
        self.assertIn('http://', self.session.adapters)

    def test_exception(self):
        with patch('requests.Session.send', side_effect=RequestException) as mock_send:
            with self.assertRaises(RequestException):
                self.session.get(self.url)

if __name__ == '__main__':
    unittest.main()