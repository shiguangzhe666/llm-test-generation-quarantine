import pytest
from requests.auth import HTTPBasicAuth, HTTPProxyAuth, HTTPDigestAuth

def test_HTTPBasicAuth_init():
    auth = HTTPBasicAuth('username', 'password')
    assert auth.username == 'username'
    assert auth.password == 'password'

def test_HTTPBasicAuth_call():
    r = mock.Mock()
    auth = HTTPBasicAuth('username', 'password')
    auth(r)
    assert r.headers['Authorization'] == _basic_auth_str('username', 'password')

def test_HTTPProxyAuth_init():
    auth = HTTPProxyAuth('username', 'password')
    assert auth.username == 'username'
    assert auth.password == 'password'

def test_HTTPProxyAuth_call():
    r = mock.Mock()
    auth = HTTPProxyAuth('username', 'password')
    auth(r)
    assert r.headers['Proxy-Authorization'] == _basic_auth_str('username', 'password')

def test_HTTPDigestAuth_init():
    auth = HTTPDigestAuth('username', 'password')
    assert auth.username == 'username'
    assert auth.password == 'password'

def test_HTTPDigestAuth_build_digest_header():
    auth = HTTPDigestAuth('username', 'password')
    r = mock.Mock()
    r.headers['www-authenticate'] = 'Digest realm="testrealm", nonce="1234"'
    assert auth.build_digest_header(r) == 'Digest username="username", realm="testrealm", nonce="1234"'

def test_HTTPDigestAuth_handle_401():
    auth = HTTPDigestAuth('username', 'password')
    r = mock.Mock()
    r.headers['www-authenticate'] = 'Digest realm="testrealm", nonce="1234"'
    r.content = b''
    r.raw = mock.Mock()
    r.raw.release_conn = mock.Mock()
    r.request = mock.Mock()
    r.request.copy = mock.Mock()
    r.request.copy.return_value = r.request
    r.request.prepare_cookies = mock.Mock()
    r.request.prepare_cookies.return_value = r.request
    r.connection = mock.Mock()
    r.connection.send = mock.Mock()
    r.connection.send.return_value = r
    r.history = []
    r.request = r.request
    auth.handle_401(r)
    assert r.headers['Authorization'] == auth.build_digest_header(r)

def test_HTTPDigestAuth_call():
    r = mock.Mock()
    auth = HTTPDigestAuth('username', 'password')
    auth(r)
    assert r.headers['Authorization'] == auth.build_digest_header(r)