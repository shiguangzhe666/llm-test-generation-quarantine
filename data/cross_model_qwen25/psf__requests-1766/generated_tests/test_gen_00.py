import pytest
from requests.auth import HTTPBasicAuth, HTTPProxyAuth, HTTPDigestAuth
from requests.models import Request
from requests.structures import CaseInsensitiveDict

def test_httpbasicauth():
    auth = HTTPBasicAuth('user', 'pass')
    r = Request('GET', 'http://example.com')
    auth(r)
    assert r.headers['Authorization'] == 'Basic dXNlcjpwYXNz'

def test_httpproxyauth():
    auth = HTTPProxyAuth('user', 'pass')
    r = Request('GET', 'http://example.com')
    auth(r)
    assert r.headers['Proxy-Authorization'] == 'Basic dXNlcjpwYXNz'

def test_httpdigestauth():
    auth = HTTPDigestAuth('user', 'pass')
    r = Request('GET', 'http://example.com')
    auth(r)
    assert r.headers['Authorization'] == 'Digest realm="Example Realm", ' \
                                         'nonce="randomnonce", uri="/", ' \
                                         'response="digestresponse", ' \
                                         'qop="auth", ' \
                                         'nc=00000001, ' \
                                         'cnonce="randomcnonce"'

def test_httpdigestauth_handle_401():
    auth = HTTPDigestAuth('user', 'pass')
    r = Request('GET', 'http://example.com')
    r.register_hook('response', auth.handle_401)
    auth.handle_401(r)
    assert r.headers['Authorization'] == 'Digest realm="Example Realm", ' \
                                         'nonce="randomnonce", uri="/", ' \
                                         'response="digestresponse", ' \
                                         'qop="auth", nc=00000001, ' \
                                         'cnonce="randomcnonce"'

def test_httpdigestauth_handle_401_no_nonce():
    auth = HTTPDigestAuth('user', 'pass')
    auth.last_nonce = ''
    r = Request('GET', 'http://example.com')
    r.register_hook('response', auth.handle_401)
    auth.handle_401(r)
    assert r.headers['Authorization'] == 'Digest realm="Example Realm", ' \
                                         'nonce="randomnonce", uri="/", ' \
                                         'response="digestresponse", ' \
                                         'qop="auth", nc=00000001, ' \
                                         'cnonce="randomcnonce"'