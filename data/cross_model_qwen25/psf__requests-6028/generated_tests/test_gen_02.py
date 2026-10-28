import os
import socket
from urllib.parse import urlparse
from requests.packages.urllib3.util import url as urllib3_url

def test_address_in_network():
    assert urllib3_url.address_in_network("192.168.1.1", "192.168.1.0/24")
    assert not urllib3_url.address_in_network("192.168.1.1", "192.168.100.0/24")
    assert urllib3_url.address_in_network("192.168.1.1", "192.168.1.1/32")

def test_dotted_netmask():
    assert dotted_netmask(24) == "255.255.255.0"
    assert dotted_netmask(32) == "255.255.255.255"

def test_is_ipv4_address():
    assert urllib3_url.is_ipv4_address("192.168.1.1")
    assert not urllib3_url.is_ipv4_address("not an ip")

def test_is_valid_cidr():
    assert urllib3_url.is_valid_cidr("192.168.1.0/24")
    assert not urllib3_url.is_valid_cidr("192.168.1.0")
    assert not urllib3_url.is_valid_cidr("192.168.1.0/33")

def test_should_bypass_proxies():
    with set_environ('no_proxy', 'example.com,192.168.1.0/24'):
        assert urllib3_url.should_bypass_proxies('http://example.com', 'example.com')
        assert not urllib3_url.should_bypass_proxies('http://192.168.1.1', 'example.com')
        assert not urllib3_url.should_bypass_proxies('http://192.168.2.1', 'example.com')

def test_get_environ_proxies():
    with set_environ('no_proxy', 'example.com,192.168.1.0/24'):
        proxies = urllib3_url.get_environ_proxies('http://example.com')
        assert proxies.get('http') is None
        assert proxies.get('https') is None

        proxies = urllib3_url.get_environ_proxies('http://192.168.1.1')
        assert proxies.get('http') is None
        assert proxies.get('https') is None

        proxies = urllib3_url.get_environ_proxies('http://192.168.2.1')
        assert proxies.get('http') == 'http://proxy.example.com'
        assert proxies.get('https') == 'http://proxy.example.com'

if __name__ == '__main__':
    test_address_in_network()
    test_dotted_netmask()
    test_is_ipv4_address()
    test_is_valid_cidr()
    test_should_bypass_proxies()
    test_get_environ_proxies()