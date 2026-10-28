import pytest
from requests.auth import HTTPBasicAuth, HTTPProxyAuth, HTTPDigestAuth, _basic_auth_str
from unittest.mock import patch

def test_basic_auth_str():
    username = 'test_user'
    password = 'test_password'
    expected_result = 'Basic dGVzdF91c2VyOnRlc3QtcGFzc3dvcmQ='
    assert _basic_auth_str(username, password) == expected_result

def test_http_basic_auth():
    username = 'test_user'
    password = 'test_password'
    auth = HTTPBasicAuth(username, password)
    r = auth(None)
    assert r.headers['Authorization'] == 'Basic dGVzdF91c2VyOnRlc3QtcGFzc3dvcmQ='

def test_http_proxy_auth():
    username = 'test_user'
    password = 'test_password'
    auth = HTTPProxyAuth(username, password)
    r = auth(None)
    assert r.headers['Proxy-Authorization'] == 'Basic dGVzdF91c2VyOnRlc3QtcGFzc3dvcmQ='

@patch('requests.auth.hashlib.md5')
def test_http_digest_auth(mock_md5):
    username = 'test_user'
    password = 'test_password'
    auth = HTTPDigestAuth(username, password)
    mock_md5.return_value.hexdigest.return_value = 'hashed_password'
    r = auth(None)
    assert r.headers['Authorization'] == 'Digest username="test_user", realm="", nonce="", uri="", response="hashed_password"'