import unittest
import os
import socket
from urllib.parse import urlparse

from your_module import (
    unquote_unreserved, requote_uri, address_in_network,
    dotted_netmask, is_ipv4_address, is_valid_cidr,
    set_environ, should_bypass_proxies, get_environ_proxies
)

class TestYourModule(unittest.TestCase):

    def test_unquote_unreserved(self):
        self.assertEqual(unquote_unreserved('%20'), ' ')
        self.assertEqual(unquote_unreserved('%21'), 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-._~')
        self.assertEqual(unquote_unreserved('%E2%82%AC'), '€')

    def test_requote_uri(self):
        self.assertEqual(requote_uri('ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-._~'), 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-._~')
        self.assertEqual(requote_uri('%20'), '%20')

    def test_address_in_network(self):
        self.assertTrue(address_in_network('192.168.1.1', '192.168.1.0/24'))
        self.assertFalse(address_in_network('192.168.1.1', '192.168.100.0/24'))

    def test_dotted_netmask(self):
        self.assertEqual(dotted_netmask(24), '255.255.255.0')

    def test_is_ipv4_address(self):
        self.assertTrue(is_ipv4_address('192.168.1.1'))
        self.assertFalse(is_ipv4_address('::1'))

    def test_is_valid_cidr(self):
        self.assertTrue(is_valid_cidr('192.168.1.1/24'))
        self.assertFalse(is_valid_cidr('192.168.1.1/33'))

    def test_set_environ(self):
        with set_environ('TEST_ENV', 'test_value'):
            self.assertEqual(os.environ.get('TEST_ENV'), 'test_value')
        self.assertIsNone(os.environ.get('TEST_ENV'))

    def test_should_bypass_proxies(self):
        self.assertTrue(should_bypass_proxies('http://localhost', 'localhost,127.0.0.1'))
        self.assertFalse(should_bypass_proxies('http://google.com', 'localhost,127.0.0.1'))

    def test_get_environ_proxies(self):
        self.assertIsNone(get_environ_proxies('http://localhost'))
        self.assertIsNone(get_environ_proxies('http://google.com'))

if __name__ == '__main__':
    unittest.main()

import struct
import socket
import os
import contextlib
from urllib.parse import urlparse

UNRESERVED_SET = set('ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-._~')

def unquote_unreserved(uri):
    parts = uri.split('%')
    for i in range(1, len(parts)):
        h = parts[i][0:2]
        if len(h) == 2 and h.isalnum():
            try:
                c = chr(int(h, 16))
            except ValueError:
                raise InvalidURL("Invalid percent-escape sequence:  '%s'" % h)

            if c in UNRESERVED_SET:
                parts[i] = c + parts[i][2:]
            else:
                parts[i] = '%%%s' % parts[i][2:]
        else:
            parts[i] = '%%%s' % parts[i]
    return ''.join(parts)

def requote_uri(uri):
    safe_with_percent = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-._~"
    safe_without_percent = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-._~"
    try:
        return quote(unquote_unreserved(uri), safe=safe_with_percent)
    except InvalidURL:
        return quote(uri, safe=safe_without_percent)

def address_in_network(ip, net):
    ipaddr = struct.unpack('=L', socket.inet_aton(ip))[0]
    netaddr, bits = net.split('/')
    netmask = struct.unpack('=L', socket.inetat.inet_aton(dotted_netmask(int(bits))))[0]
    network = struct.unpack('=L', socket.inet_aton(netaddr))[0] & netmask
    return (ipaddr & netmask) == (network & netmask)

def dotted_netmask(mask):
    bits = 0xffffffff ^ (1 << 32 - mask) - 1
    return socket.inet_ntoa(struct.pack('>I', bits))

def is_ipv4_address(string_ip):
    try:
        socket.inet_aton(string_ip)
    except socket.error:
        return False
    return True

def is_valid_cidr(string_network):
    if string_network.count('/') == 1:
        try:
            mask = int(string_network.split('/')[1])
        except ValueError:
            return False

        if mask < 1 or mask > 32:
            return False

        try:
            socket.inet_aton(string_network.split('/')[0])
        except socket.error:
            return False
    else:
        return False
    return True

@contextlib.contextmanager
def set_environ(env_name, value):
    value_changed = value is not None
    if value_changed:
        old_value = os.environ.get(env_name)
        os.environ[env_name] = value
    try:
        yield
    finally:
        if value_changed:
            if old_value is None:
                del os.environ[env_name]
            else:
                os.environ[env_name] = old_value

def should_bypass_proxies(url, no_proxy):
    get_proxy = lambda k: os.environ.get(k) or os.environ.get(k.upper())

    no_proxy_arg = no_proxy
    if no_proxy is None:
        no_proxy = get_proxy('no_proxy')
    parsed = urlparse(url)

    if parsed.hostname is None:
        return True

    if no_proxy:
        no_proxy = (
            host for host in no_proxy.replace('  ', '').split(',') if host
        )

        if is_ipv4_address(parsed.hostname):
            for proxy_ip in no_proxy:
                if is_valid_cidr(proxy_ip):
                    if address_in_network(parsed.hostname, proxy_ip):
                        return True
        return False

def get_environ_proxies(url):
    pass

import struct
import socket
import os
import contextlib
from urllib.parse import urlparse

UNRESERVED_SET = set('ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-._~')

def unquote_unreserved(uri):
    parts = uri.split('%')
    for i in range(1, len(parts)):
        h = parts[i][0:2]
        if len(h) == 2 and h.isalnum():
            try:
                c = chr(int(h, 16))
            except ValueError:
                raise InvalidURL("Invalid percent-escape sequence:  '%s'" % h)

            if c in UNRESERVED_SET:
                parts[i] = c + parts[i][2:]
            else:
                parts[i] = '%%%s' % parts[i][2:]
        else:
            parts[i] = '%%%s' % parts[i]
    return ''.join(parts)

def requote_uri(uri):
    safe_with_percent = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-._~"
    safe_without_percent = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-._~"
    try:
        return quote(unquote_unreserved(uri), safe=safe_with_percent)
    except InvalidURL:
        return quote(uri, safe=safe_without_percent)

def address_in_network(ip, net):
    ipaddr = struct.unpack('=L', socket.inet_aton(ip))[0]
    netaddr, bits = net.split('/')
    netmask = struct.unpack('=L', socket.inet_aton(dotted_netmask(int(bits))))[0]
    network = struct.unpack('=L', socket.inet_aton(netaddr))[0] & netmask
    return (ipaddr & netmask) == (network & netmask)

def dotted_netmask(mask):
    bits = 0xffffffff ^ (1 << 32 - mask) - 1
    return socket.inet_ntoa(struct.pack('>I', bits))

def is_ipv4_address(string_ip):
    try:
        socket.inet_aton(string_ip)
    except socket.error:
        return False
    return True

def is_valid_cidr(string_network):
    if string_network.count('/') == 1:
        try:
            mask = int(string_network.split('/')[1])
        except ValueError:
            return False

        if mask < 1 or mask > 32:
            return False

        try:
            socket.inet_aton(string_network.split('/')[0])
        except socket.error:
            return False
    else:
        return False
    return True

@contextlib.contextmanager
def set_environ(env_name, value):
    value_changed = value is not None
    if value_changed:
        old_value = os.environ.get(env_name)
        os.environ[env_name] = value
    try:
        yield
    finally:
        if value_changed:
            if old_value is None:
                del os.environ[env_name]
            else:
                os.environ[env_name] = old_value

def should_bypass_proxies(url, no_proxy):
    get_proxy = lambda k: os.environ.get(k) or os.environ.get(k.upper())

    no_proxy_arg = no_proxy
    if no_proxy is None:
        no_proxy = get_proxy('no_proxy')
    parsed = urlparse(url)

    if parsed.hostname is None:
        return True

    if no_proxy:
        no_proxy = (
            host for host in no_proxy.replace('  ', '').split(',') if host
        )

        if is_ipv4_address(parsed.hostname):
            for proxy_ip in no_proxy:
                if is_valid_cidr(proxy_ip):
                    if address_in_network(parsed.hostname, proxy_ip):
                        return True
        return False

def get_environ_proxies(url):
    pass