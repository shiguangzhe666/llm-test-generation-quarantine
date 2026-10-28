import pytest
from requests.auth import HTTPBasicAuth, HTTPProxyAuth, HTTPDigestAuth

def test_http_basic_auth_class():
    auth = HTTPBasicAuth('username', 'password')
    assert isinstance(auth, HTTPBasicAuth)

def test_http_basic_auth_call():
    auth = HTTPBasicAuth('username', 'password')
    request = {}
    auth_header = auth(request)
    assert auth_header['Authorization'] == 'Basic dXNlcm5hbWU6cGFzc3dvcmQ='

def test_http_proxy_auth_class():
    auth = HTTPProxyAuth('username', 'password')
    assert isinstance(auth, HTTPProxyAuth)

def test_http_proxy_auth_call():
    auth = HTTPProxyAuth('username', 'password')
    request = {}
    auth_header = auth(request)
    assert auth_header['Proxy-Authorization'] == 'Basic dXNlcm5hbWU6cGFzc3dvcmQ='

def test_http_digest_auth_class():
    auth = HTTPDigestAuth('username', 'password')
    assert isinstance(auth, HTTPDigestAuth)

def test_http_digest_auth_call():
    auth = HTTPDigestAuth('username', 'password')
    request = {}
    auth_header = auth(request)
    assert auth_header['Authorization'] == 'Digest username="username", realm="", nonce="", uri="", response=""'

def test_http_digest_auth_handle_401():
    auth = HTTPDigestAuth('username', 'password')
    response = {}
    auth_header = auth.handle_401(response)
    assert auth_header == response

def test_http_digest_auth_handle_401_with_nonce():
    auth = HTTPDigestAuth('username', 'password')
    response = {}
    auth_header = auth.handle_401(response, nonce='nonce')
    assert auth_header['Authorization'] == 'Digest username="username", realm="", nonce="nonce", uri="", response=""'

def test_http_digest_auth_build_digest_header():
    auth = HTTPDigestAuth('username', 'password')
    header = auth.build_digest_header('GET', 'http://example.com')
    assert header == 'Digest username="username", realm="", nonce="", uri="http://example.com", response=""'

def test_http_digest_auth_build_digest_header_with_qop():
    auth = HTTPDigestAuth('username', 'password')
    header = auth.build_digest_header('GET', 'http://example.com', qop='auth')
    assert header == 'Digest username="username", realm="", nonce="", uri="http://example.com", response="", qop=auth, nc=00000001, cnonce=""'