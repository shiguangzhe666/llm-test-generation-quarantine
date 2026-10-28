import os
import socket
from urllib.parse import urlparse

def test_should_bypass_proxies():
    # Mocking environment variables
    with set_environ('no_proxy', 'localhost,127.0.0.1,::1,192.168.1.0/24'):
        assert should_bypass_proxies('http://localhost:8080', None) == True
        assert should_bypass_proxies('http://127.0.0.1:8080', None) == True
        assert should_bypass_proxies('http://::1:8080', None) == True
        assert should_bypass_proxies('http://192.168.1.1:8080', None) == True
        assert should_bypass_proxies('http://192.168.100.1:8080', None) == False
        assert should_bypass_proxies('http://example.com:8080', None) == False

def test_get_environ_proxies():
    # Mocking environment variables
    with set_environ('no_proxy', 'localhost,127.0.0.1,::1,192.168.1.0/24'):
        proxies = get_environ_proxies('http://192.168.1.1:8080', None)
        assert proxies['no-proxy'] == 'localhost,127.0.0.1,::1,192.168.1.0/24'

        proxies = get_environ_proxies('http://example.com:8080', None)
        assert proxies['no-proxy'] == 'localhost,127.0.0.1,::1,192.168.1.0/24'

if __name__ == '__main__':
    test_should_bypass_proxies()
    test_get_environ_proxies()