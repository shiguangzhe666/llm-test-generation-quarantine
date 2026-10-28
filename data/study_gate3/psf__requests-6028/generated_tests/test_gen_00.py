import unittest
import socket
import struct
import os
import contextlib
import warnings
import urllib.parse as urlparse
from unittest.mock import patch, MagicMock
import requests
import codecs
import sys

class TestEncodingFunctions(unittest.TestCase):
    def test_get_encoding_from_headers(self):
        # Test with charset in content-type
        headers = {'content-type': 'text/html; charset=utf-8'}
        self.assertEqual(get_encoding_from_headers(headers), 'utf-8')
        
        # Test text without charset
        headers = {'content-type': 'text/plain'}
        self.assertEqual(get_encoding_from_headers(headers), 'ISO-8859-1')
        
        # Test application/json
        headers = {'content-type': 'application/json'}
        self.assertEqual(get_encoding_from_headers(headers), 'utf-8')
        
        # Test missing content-type
        headers = {}
        self.assertIsNone(get_encoding_from_headers(headers))

class TestStreamDecode(unittest.TestCase):
    def test_stream_decode(self):
        # Test with utf-8 encoding
        iterator = [b'hello', b'world']
        r = MagicMock()
        r.encoding = 'utf-8'
        result = list(stream_decode_response_unicode(iterator, r))
        self.assertEqual(''.join(result), 'helloworld')
        
        # Test with invalid encoding
        r.encoding = 'invalid'
        with self.assertRaises(UnicodeError):
            list(stream_decode_response_unicode(iterator, r))

class TestIterSlices(unittest.TestCase):
    def test_iter_slices(self):
        self.assertEqual(list(iter_slices('abcdef', 2)), ['ab', 'cd', 'ef'])
        self.assertEqual(list(iter_slices('abcdef', 10)), ['abcdef'])
        self.assertEqual(list(iter_slices('a', 1)), ['a'])

class TestGetUnicodeFromResponse(unittest.TestCase):
    def test_get_unicode_from_response(self):
        r = MagicMock()
        r.content = b'hello'
        r.encoding = 'utf-8'
        self.assertEqual(get_unicode_from_response(r), 'hello')
        
        r.encoding = 'invalid'
        with self.assertRaises(UnicodeError):
            get_unicode_from_response(r)
        
        r.encoding = None
        self.assertEqual(get_unicode_from_response(r), 'hello')

class TestUnquoteUnreserved(unittest.TestCase):
    def test_unquote_unreserved(self):
        self.assertEqual(unquote_unreserved('http%3A%2F%2Fexample.com'), 'http://example.com')
        self.assertEqual(unquote_unreserved('http%3A%2F%2Fexample.com%3Fquery%3D1'), 'http://example.com?query=1')
        self.assertEqual(unquote_unreserved('http%3A%2F%2Fexample.com%252520'), 'http://example.com%2520')

class TestRequoteUri(unittest.TestCase):
    def test_requote_uri(self):
        self.assertEqual(requote_uri('http://example.com/path?query=1'), 'http://example.com/path?query=1')
        self.assertEqual(requote_uri('http://example.com/path?query=1%20'), 'http://example.com/path?query=1%20')

class TestAddressInNetwork(unittest.TestCase):
    def test_address_in_network(self):
        self.assertTrue(address_in_network('192.168.1.1', '192.168.1.0/24'))
        self.assertFalse(address_in_network('192.168.2.1', '192.168.1.0/24'))

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
        self.assertFalse(is_valid_cidr('192.168.1.0/24:1'))

class TestSetEnviron(unittest.TestCase):
    @patch('os.environ')
    def test_set_environ(self, mock_env):
        with contextlib.chdir('/test'):
            with set_environ('TEST_VAR', 'value'):
                self.assertEqual(os.environ['TEST_VAR'], 'value')
            self.assertEqual(os.environ['TEST_VAR'], 'value')

class TestShouldBypassProxies(unittest.TestCase):
    @patch('requests.utils.proxy_bypass')
    def test_should_bypass_proxies(self, mock_proxy_bypass):
        mock_proxy_bypass.return_value = True
        self.assertTrue(should_bypass_proxies('http://example.com'))
        
        mock_proxy_bypass.return_value = False
        self.assertFalse(should_bypass_proxies('http://example.com'))
        
        self.assertTrue(should_bypass_proxies('http://192.168.1.1'))
        self.assertTrue(should_bypass_proxies('http://192.168.1.0/24'))
        self.assertTrue(should_bypass_proxies('http://example.com/path'))