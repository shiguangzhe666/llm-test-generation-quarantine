import unittest
from unittest import mock
import os
import socket
import struct
import urllib.parse as urlparse
from contextlib import contextmanager
import requests
import codecs
from requests.utils import parse_contentDisposition
from requests.models import Response
from requests import exceptions

class TestEncodingFunctions(unittest.TestCase):
    def test_get_encoding_from_headers(self):
        headers = {'content-type': 'text/html; charset=utf-8'}
        self.assertEqual(get_encoding_from_headers(headers), 'utf-8')

        headers = {'content-type': 'text/html'}
        self.assertEqual(get_encoding_from_headers(headers), 'ISO-8859-1')

        headers = {'content-type': 'application/json'}
        self.assertEqual(get_encoding_from_headers(headers), 'utf-8')

        headers = {'content-type': ''}
        self.assertIsNone(get_encoding_from_headers(headers))

    def test_stream_decode_response_unicode(self):
        mock_iterator = iter([b'Hello', b'World'])
        r = mock.Mock()
        r.encoding = 'utf-8'
        decoder = codecs.getincrementaldecoder('utf-8')(errors='replace')
        with mock.patch('codecs.getincrementaldecoder', return_value=decoder):
            result = list(stream_decode_response_unicode(mock_iterator, r))
            self.assertEqual(result, ['Hello', 'World'])

    def test_iter_slices(self):
        self.assertEqual(list(iter_slices("abcdef", 2)), ["ab", "cd", "ef"])
        self.assertEqual(list(iter_slices("abc", 5)), ["abc"])
        self.assertEqual(list(iter_slices("", 1)), [])

    def test_get_unicode_from_response(self):
        r = mock.Mock()
        r.content = b"Hello"
        r.encoding = 'utf-8'
        self.assertEqual(get_unicode_from_response(r), "Hello")

        r.encoding = None
        self.assertEqual(get_unicode_from_response(r), "Hello")

        r.encoding = 'utf-8'
        with self.assertRaises(UnicodeError):
            get_unicode_from_response(r)

        r.encoding = 'utf-8'
        self.assertEqual(get_unicode_from_response(r), "Hello")

class TestURIFunctions(unittest.TestCase):
    def test_unquote_unreserved(self):
        self.assertEqual(unquote_unreserved("http%3A%2F%2Fexample.com"), "http://example.com")
        self.assertEqual(unquote_unreserved("http%3A%2F%2Fexample.com%3Fquery%3Dparam"), "http://example.com?query=param")
        self.assertEqual(unquote_unreserved("http%3A%2F%2Fexample.com%23fragment"), "http://example.com#fragment")

    def test_requote_uri(self):
        self.assertEqual(requote_uri("http://example.com"), "http://example.com")
        self.assertEqual(requote_uri("http://example.com/path?query=param#fragment"), "http://example.com/path?query=param#fragment")
        self.assertEqual(requote_uri("http://example.com/path%20with%20space"), "http://example.com/path with space")

class TestIPFunctions(unittest.TestCase):
    def test_address_in_network(self):
        self.assertTrue(address_in_network("192.168.1.1", "192.168.1.0/24"))
        self.assertFalse(address_in_network("192.168.1.1", "192.168.100.0/24"))

    def test_dotted_netmask(self):
        self.assertEqual(dotted_netmask(24), "255.255.255.0")
        self.assertEqual(dotted_netmask(16), "255.255.0.0")
        self.assertEqual(dotted_netmask(8), "255.0.0.0")

    def test_is_ipv4_address(self):
        self.assertTrue(is_ipv4_address("192.168.1.1"))
        self.assertFalse(is_ipv4_address("192.168.1"))

    def test_is_valid_cidr(self):
        self.assertTrue(is_valid_cidr("192.168.1.0/24"))
        self.assertFalse(is_valid_cidr("192.168.1.0/33"))
        self.assertFalse(is_valid_cidr("192.168.1.0/24:123"))

class TestEnvironFunctions(unittest.TestCase):
    def test_set_environ(self):
        with set_environ("TEST_VAR", "test_value"):
            self.assertEqual(os.environ.get("TEST_VAR"), "test_value")
        self.assertNotIn("TEST_VAR", os.environ)

    def test_should_bypass_proxies(self):
        with mock.patch('os.environ', {'no_proxy': '192.168.1.0/24'}):
            self.assertTrue(should_bypass_proxies("http://192.168.1.1", "192.168.1.0/24"))
            self.assertTrue(should_bypass_proxies("http://192.168.1.1:8080", "192.168.1.0/24"))
            self.assertFalse(should_bypass_proxies("http://192.168.2.1", "192.168.1.0/24"))