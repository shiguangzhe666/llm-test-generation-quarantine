import os
import socket
import pytest
from requests.compat import urlparse, unquote_unreserved, requote_uri, is_ipv4_address, is_valid_cidr, address_in_network, dotted_netmask, set_environ, should_bypass_proxies

def test_unquote_unreserved():
    assert unquote_unreserved('%7E') == '~'
    assert unquote_unreserved('%7Efoo') == '~foo'
    assert unquote_unreserved('%7E%25') == '~%'

def test_requote_uri():
    assert requote_uri('http://example.com/%7Efoo') == 'http://example.com/%7Efoo'
    assert requote_uri('http://example.com/%7Efoo/') == 'http://example.com/%7Efoo/%2F'
    assert requote_uri('http://example.com/%7Efoo%20bar/') == 'http://example.com/%7Efoo%20bar/%2F'

def test_is_ipv4_address():
    assert is_ipv4_address('192.168.1.1') is True
    assert is_ipv4_address('2001:0db8:85a3:0000:0000:8a2e:0370:7334') is False

def test_is_valid_cidr():
    assert is_valid_cidr('192.168.1.0/24') is True
    assert is_valid_cidr('192.168.100.0/24') is False
    assert is_valid_cidr('192.168.1.0/32') is True
    assert is_valid_cidr('192.168.1.0/33') is False

def test_dotted_netmask():
    assert dotted_netmask(24) == '255.255.255.0'
    assert dotted_netmask(32) == '255.255.255.255'

def test_address_in_network():
    assert address_in_network('192.168.1.1', '192.168.1.0/24') is True
    assert address_in_network('192.168.2.1', '192.168.1.0/24') is False

def test_should_bypass_proxies():
    assert should_bypass_proxies('http://example.com', 'example.com') is True
    assert should_bypass_proxies('http://example.com', 'example.org') is False
    assert should_bypass_proxies('http://192.168.1.1', '192.168.1.0/24') is True
    assert should_bypass_proxies('http://192.168.2.1', '192.168.1.0/24') is False

def test_set_environ():
    with set_environ('TEST_VAR', 'test_value'):
        assert os.environ['TEST_VAR'] == 'test_value'
    assert 'TEST_VAR' not in os.environ

    with set_environ('TEST_VAR', None):
        assert 'TEST_VAR' not in os.environ

    with set_environ('TEST_VAR', 'test_value'):
        assert os.environ['TEST_VAR'] == 'test_value'
    assert 'TEST_VAR' not in os.environ

    with set_environ('TEST_VAR', 'test_value2'):
        assert os.environ['TEST_VAR'] == 'test_value2'
    assert 'TEST_VAR' not in os.environ