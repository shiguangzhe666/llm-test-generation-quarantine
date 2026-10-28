import unittest
import os
from unittest.mock import patch
from urllib.parse import urlparse

class TestProxyMethods(unittest.TestCase):

    def test_set_environ(self):
        with patch.dict(os.environ, {'MY_VAR': 'old_value'}, clear=True):
            with set_environ('MY_VAR', 'new_value'):
                self.assertEqual(os.getenv('MY_VAR'), 'new_value')
            self.assertEqual(os.getenv('MY_VAR'), 'old_value')

        with patch.dict(os.environ, {'MY_VAR': 'old_value'}, clear=True):
            with set_environ('MY_VAR', None):
                self.assertNotIn('MY_VAR', os.environ)
            self.assertEqual(os.getenv('MY_VAR'), 'old_value')

    def test_is_ipv4_address(self):
        self.assertTrue(is_ipv4_address('192.168.1.1'))
        self.assertFalse(is_ipv4_address('2001:0db8:85a3:0000:0000:8a2e:0370:7334'))
        self.assertFalse(is_ipv4_address('localhost'))

    def test_is_valid_cidr(self):
        self.assertTrue(is_valid_cidr('192.168.1.1/24'))
        self.assertFalse(is_valid_cidr('192.168.1.1/33'))
        self.assertFalse(is_valid_cidr('192.168.1.1/abc'))

    def test_address_in_network(self):
        self.assertTrue(address_in_network('192.168.1.1', '192.168.1.0/24'))
        self.assertFalse(address_in_network('192.168.1.1', '192.168.1.0/24'))

    def test_should_bypass_proxies(self):
        self.assertTrue(should_bypass_proxies('http://192.168.1.1', '192.168.1.0/24'))
        self.assertFalse(should_bypass_proxies('http://google.com', '192.168.1.0/24'))

if __name__ == '__main__':
    unittest.main()