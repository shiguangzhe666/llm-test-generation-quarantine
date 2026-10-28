import pytest
from requests.auth import _basic_auth_str, HTTPBasicAuth, HTTPDigestAuth, HTTPProxyAuth

def test_basic_auth_str():
    assert _basic_auth_str('username', 'password') == 'Basic dXNlcm5hbWU6cGFzc3dvcmQ='

def test_http_basic_auth_call():
    auth = HTTPBasicAuth('username', 'password')
    r = auth(object())
    assert r.headers['Authorization'] == 'Basic dXNlcm5hbWU6cGFzc3dvcmQ='

def test_http_proxy_auth_call():
    auth = HTTPProxyAuth('username', 'password')
    r = auth(object())
    assert r.headers['Proxy-Authorization'] == 'Basic dXNlcm5hbWU6cGFzc3dvcmQ='

def test_http_digest_auth_call():
    auth = HTTPDigestAuth('username', 'password')
    r = auth(object())
    assert 'Authorization' in r.headers

def test_http_digest_auth_handle_401():
    auth = HTTPDigestAuth('username', 'password')
    r = auth(object())
    r.status_code = 401
    r.headers['www-authenticate'] = 'Digest realm="test", nonce="123"'
    r = auth.handle_401(r)
    assert 'Authorization' in r.headers