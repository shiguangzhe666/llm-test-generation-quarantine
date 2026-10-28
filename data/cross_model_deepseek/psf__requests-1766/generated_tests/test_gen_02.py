import pytest
from requests.auth import HTTPBasicAuth, HTTPProxyAuth, HTTPDigestAuth, _basic_auth_str

def test_basic_auth_str():
    assert _basic_auth_str('username', 'password') == 'Basic dXNlcm5hbWU6cGFzc3dvcmQ='

def test_http_basic_auth():
    auth = HTTPBasicAuth('username', 'password')
    r = auth(object())
    assert r.headers['Authorization'] == 'Basic dXNlcm5hbWU6cGFzc3dvcmQ='

def test_http_proxy_auth():
    auth = HTTPProxyAuth('username', 'password')
    r = auth(object())
    assert r.headers['Proxy-Authorization'] == 'Basic dXNlcm5hbWU6cGFzc3dvcmQ='

def test_http_digest_auth():
    auth = HTTPDigestAuth('username', 'password')
    r = auth(object())
    assert 'Authorization' not in r.headers
    r.headers['www-authenticate'] = 'Digest realm="test", nonce="1234"'
    r = auth(r)
    assert r.headers['Authorization'] == 'Digest username="username", realm="test", nonce="1234", uri="", response=""'

def test_http_digest_auth_401():
    auth = HTTPDigestAuth('username', 'password')
    r = auth(object())
    r.status_code = 401
    r.headers['www-authenticate'] = 'Digest realm="test", nonce="1234"'
    r = auth.handle_401(r)
    assert r.headers['Authorization'] == 'Digest username="username", realm="test", nonce="1234", uri="", response=""'