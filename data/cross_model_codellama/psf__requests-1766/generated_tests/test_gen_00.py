import pytest

from requests import HTTPBasicAuth, HTTPProxyAuth, HTTPDigestAuth


def test_HTTPBasicAuth():
    auth = HTTPBasicAuth('username', 'password')
    assert auth.username == 'username'
    assert auth.password == 'password'


def test_HTTPProxyAuth():
    auth = HTTPProxyAuth('username', 'password')
    assert auth.username == 'username'
    assert auth.password == 'password'


def test_HTTPDigestAuth():
    auth = HTTPDigestAuth('username', 'password')
    assert auth.username == 'username'
    assert auth.password == 'password'


def test_HTTPDigestAuth_build_digest_header():
    auth = HTTPDigestAuth('username', 'password')
    method = 'GET'
    url = 'http://www.example.com'
    header = auth.build_digest_header(method, url)
    assert header.startswith('Digest')
    assert 'username' in header
    assert 'realm' in header
    assert 'nonce' in header
    assert 'uri' in header
    assert 'response' in header


def test_HTTPDigestAuth_handle_401():
    auth = HTTPDigestAuth('username', 'password')
    r = {'headers': {'www-authenticate': 'digest realm="Test Realm", nonce="12345"'}}
    new_r = auth.handle_401(r)
    assert new_r == r


def test_HTTPDigestAuth_handle_401_with_saved_nonce():
    auth = HTTPDigestAuth('username', 'password')
    auth.last_nonce = '12345'
    r = {'headers': {'www-authenticate': 'digest realm="Test Realm", nonce="12345"'}}
    new_r = auth.handle_401(r)
    assert new_r != r


def test_HTTPDigestAuth_handle_401_with_multiple_401_calls():
    auth = HTTPDigestAuth('username', 'password')
    r = {'headers': {'www-authenticate': 'digest realm="Test Realm", nonce="12345"'}}
    new_r = auth.handle_401(r)
    assert new_r == r
    new_r = auth.handle_401(r)
    assert new_r != r