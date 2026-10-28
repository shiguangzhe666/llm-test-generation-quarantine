import unittest
import socket
import struct
import os
import warnings
import contextlib
from urllib.parse import urlparse
from unittest.mock import patch, MagicMock
import requests
from requests import utils
from requests.utils import get_encoding_from_headers, stream_decode_response_unicode, iter_slices, get_unicode_from_response, unquote_unreserved, requote_uri, address_in_network, dotted_netmask, is_ipv4_address, is_valid_cidr, set_environ, should_bypass_proxies, get_environ_proxies
from requests.exceptions import InvalidURL

class TestEncodingFunctions(unittest.TestCase):
    def test_get_encoding_from_headers(self):
        headers = {'content-type': 'text/html; charset=utf-8'}
        self.assertEqual(get_encoding_from_headers(headers), 'utf-8')
        
        headers = {'content-type': 'text/plain'}
        self.assertEqual(get_encoding_from_headers(headers), 'ISO-8859-1')
        
        headers = {'content-type': 'application/json'}
        self.assertEqual(get_encoding_from_headers(headers), 'utf-8')
        
        headers = {'content-type': 'application/xml; charset=ISO-8859-1'}
        self.assertEqual(get_encoding_from_headers(headers), 'ISO-8859-1')
        
        headers = {}
        self.assertIsNone(get_encoding_from_headers(headers))

class TestStreamDecode(unittest.TestCase):
    def test_stream_decode(self):
        iterator = [b'Hello', b' World']
        r = MagicMock()
        r.encoding = 'utf-8'
        result = list(stream_decode_response_unicode(iterator, r))
        self.assertEqual(''.join(result), 'Hello World')

class TestIterSlices(unittest.TestCase):
    def test_iter_slices(self):
        self.assertEqual(list(iter_slices('abcdef', 2)), ['ab', 'cd', 'ef'])
        self.assertEqual(list(iter_slices('abcdef', 10)), ['abcdef'])
        self.assertEqual(list(iter_slices('abcdef', 0)), ['abcdef'])

class TestGetUnicodeFromResponse(unittest.TestCase):
    def test_get_unicode_from_response(self):
        r = MagicMock()
        r.content = b'Hello'
        r.encoding = 'utf-8'
        self.assertEqual(get_unicode_from_response(r), 'Hello')
        
        r.encoding = None
        self.assertEqual(get_unicode_from_response(r), 'Hello')

class TestUnquoteUnreserved(unittest.TestCase):
    def test_unquote_unreserved(self):
        self.assertEqual(unquote_unreserved('http%3A%2F%2Fexample.com'), 'http://example.com')
        self.assertEqual(unquote_unreserved('http%3A%2F%2Fexample.com%3Fquery%3D1'), 'http://example.com?query=1')
        self.assertEqual(unquote_unreserved('http%3A%2F%2Fexample.com%252Fpath'), 'http://example.com%2Fpath')

class TestRequoteUri(unittest.TestCase):
    def test_requote_uri(self):
        self.assertEqual(requote_uri('http://example.com'), 'http://example.com')
        self.assertEqual(requote_uri('http://example.com/path?query=1'), 'http://example.com/path?query=1')
        self.assertEqual(requote_uri('http://example.com/path%2Fquery'), 'http://example.com/path%2Fquery')

class TestAddressInNetwork(unittest.TestCase):
    def test_address_in_network(self):
        self.assertTrue(address_in_network('192.168.1.1', '192.168.1.0/24'))
        self.assertFalse(address_in_network('192.168.1.1', '192.168.100.0/24'))

class TestDottedNetmask(unittest.TestCase):
    def test_dotted_netmask(self):
        self.assertEqual(dotted_netmask(24), '255.255.255.0')
        self.assertEqual(dotted_netmask(16), '255.255.0.0')

class TestIsIpv4Address(unittest.TestCase):
    def test_is_ipv4_address(self):
        self.assertTrue(is_ipv4_address('192.168.1.1'))
        self.assertFalse(is_ipv4_address('192.168.1'))

class TestIsValidCidr(unittest.TestCase):
    def test_is_valid_cidr(self):
        self.assertTrue(is_valid_cidr('192.168.1.0/24'))
        self.assertFalse(is_valid_cidr('192.168.1.0/33'))
        self.assertFalse(is_valid_cidr('192.168.1.0/24/'))
        self.assertFalse(is_valid_cidr('192.168.1.0'))

class TestSetEnviron(unittest.TestCase):
    def test_set_environ(self):
        with set_environ('TEST', 'value'):
            self.assertEqual(os.environ['TEST'], 'value')
        self.assertNotIn('TEST', os.environ)

class TestShouldBypassProxies(unittest.TestCase):
    @patch('requests.utils.proxy_bypass')
    def test_should_bypass_proxies(self, mock_proxy_bypass):
        mock_proxy_bypass.return_value = True
        self.assertTrue(should_bypass_proxies('http://example.com', 'example.com'))
        
        mock_proxy_bypass.return_value = False
        self.assertFalse(should_bypass_proxies('http://example.com', 'example.com'))

    def test_no_proxy_env(self):
        with patch('os.environ', {'no_proxy': 'example.com'}):
            self.assertTrue(should_bypass_proxies('http://example.com', None))

class TestGetEnvironProxies(unittest.TestCase):
    def test_get_environ_proxies(self):
        with patch('os.environ', {'http_proxy': 'http://proxy:8080', 'no_proxy': 'example.com'}):
            self.assertEqual(get_environ_proxies('http://example.com'), {})
            self.assertEqual(get_environ_proxies('http://proxy:8080'), {})
            self.assertEqual(get_environ_proxies('http://other.com'), {'http': 'http://proxy:8080'})

if __name__ == '__main__':
    unittest.main()