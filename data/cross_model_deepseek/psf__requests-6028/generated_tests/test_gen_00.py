import unittest
import os
import socket
from urllib.parse import urlparse
from . import *  # noqa: F403

class TestEnvironProxies(unittest.TestCase):

    def setUp(self):
        os.environ['http_proxy'] = 'http://proxy.example.com:3128'
        os.environ['https_proxy'] = 'https://proxy.example.com:3128'
        os.environ['no_proxy'] = 'localhost,127.0.0.1,localaddress'

    def tearDown(self):
        os.environ.pop('http_proxy', None)
        os.environ.pop('https_proxy', None)
        os.environ.pop('no_proxy', None)

    def test_should_bypass_proxies(self):
        url = 'http://localhost'
        no_proxy = 'localhost,127.0.0.1'
        result = should_bypass_proxies(url, no_proxy)
        self.assertTrue(result)

        url = 'http://127.0.0.1'
        result = should_bypass_proxies(url, no_proxy)
        self.assertTrue(result)

        url = 'http://localaddress'
        result = should_bypass_proxies(url, no_proxy)
        self.assertTrue(result)

        url = 'http://example.com'
        result = should_bypass_proxies(url, no_proxy)
        self.assertFalse(result)

    def test_is_ipv4_address(self):
        ip = '192.168.1.1'
        result = is_ipv4_address(ip)
        self.assertTrue(result)

        ip = '2001:0db8:85a3:0000:0000:8a2e:0370:7334'
        result = is_ipv4_address(ip)
        self.assertFalse(result)

    def test_is_valid_cidr(self):
        network = '192.168.1.1/24'
        result = is_valid_cidr(network)
        self.assertTrue(result)

        network = '192.168.1.1/33'
        result = is_valid_cidr(network)
        self.assertFalse(result)

        network = '192.168.1.1'
        result = is_valid_cidr(network)
        self.assertFalse(result)

    def test_address_in_network(self):
        ip = '192.168.1.1'
        network = '192.168.1.0/24'
        result = address_in_network(ip, network)
        self.assertTrue(result)

        ip = '192.168.2.1'
        network = '192.168.1.0/24'
        result = address_in_network(ip, network)
        self.assertFalse(result)

    def test_dotted_netmask(self):
        mask = 24
        result = dotted_netmask(mask)
        self.assertEqual(result, '255.255.255.0')

        mask = 16
        result = dotted_netmask(mask)
        self.assertEqual(result, '255.255.0.0')

    def test_set_environ(self):
        env_name = 'TEST_ENV'
        value = 'test_value'
        with set_environ(env_name, value):
            self.assertEqual(os.environ[env_name], value)
        self.assertNotIn(env_name, os.environ)


if __name__ == '__main__':
    unittest.main()