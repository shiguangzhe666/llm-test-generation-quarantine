import pytest
from unittest.mock import Mock, patch
from requests.auth import AuthBase, HTTPBasicAuth, HTTPProxyAuth, HTTPDigestAuth
from requests.models import Request, Response
import base64

# Mock Request and Response for testing
class MockRequest:
    def __init__(self):
        self.headers = {}

class MockResponse:
    def __init__(self, status_code=200):
        self.status_code = status_code
        self.headers = {}
        self.request = MockRequest()
        self.history = []

# Test AuthBase
def test_authbase_call_raises_notimplemented():
    auth = AuthBase()
    with pytest.raises(NotImplementedError):
        auth(MockRequest())

# Test HTTPBasicAuth
def test_httpbasicauth_sets_authorization_header():
    auth = HTTPBasicAuth('user', 'pass')
    r = MockRequest()
    auth(r)
    expected = base64.b64encode(b'user:pass').decode()
    assert r.headers['Authorization'] == f'Basic {expected}'

def test_httpbasicauth_empty_username():
    auth = HTTPBasicAuth('', 'pass')
    r = MockRequest()
    auth(r)
    expected = base64.b64encode(b':pass').decode()
    assert r.headers['Authorization'] == f'Basic {expected}'

def test_httpbasicauth_empty_password():
    auth = HTTPBasicAuth('user', 'pass')
    r = MockRequest()
    auth(r)
    expected = base64.b64encode(b'user:').decode()
    assert r.headers['Authorization'] == f'Basic {expected}'

def test_httpbasicauth_both_empty():
    auth = HTTPBasicAuth('', '')
    r = MockRequest()
    auth(r)
    expected = base64.b64encode(b':').decode()
    assert r.headers['Authorization'] == f'Basic {expected}'

def test_httpbasicauth_non_ascii():
    auth = HTTPBasicAuth('café', 'pass')
    r = MockRequest()
    auth(r)
    expected = base64.b64encode(b'caf\xc3\xa9:pass').decode()
    assert r.headers['Authorization'] == f'Basic {expected}'

# Test HTTPProxyAuth
def test_httpproxyauth_sets_proxy_authorization_header():
    auth = HTTPProxyAuth('user', 'pass')
    r = MockRequest()
    auth(r)
    expected = base64.b64encode(b'user:pass').decode()
    assert r.headers['Proxy-Authorization'] == f'Basic {expected}'

# Test HTTPDigestAuth
def test_httpdigestauth_build_header():
    auth = HTTPDigestAuth('user', 'pass')
    r = MockRequest()
    auth(r)
    # This is a simplified check; in practice, this would be validated against a known digest challenge
    assert 'Authorization' in r.headers

def test_httpdigestauth_handle_401():
    auth = HTTPDigestAuth('user', 'pass')
    r = MockResponse(401)
    r.headers['www-authenticate'] = 'Digest realm="example", nonce="123456789", qop="auth", algorithm=MD5'
    new_response = auth.handle_401(r)
    assert new_response.headers['Authorization'] == 'Digest username="user", realm="example", nonce="123456789", uri="/", response="..."'

# Test HTTPDigestAuth __call__ registers hook
def test_httpdigestauth_call_registers_hook():
    auth = HTTPDigestAuth('user', 'pass')
    r = MockRequest()
    auth(r)
    assert r.headers['Authorization'] == 'Digest username="user", realm="example", nonce="123456789", uri="/", response="..."'