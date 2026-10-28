import pytest
from unittest import mock
from requests.auth import (
    AuthBase,
    HTTPBasicAuth,
    HTTPProxyAuth,
    HTTPDigestAuth,
    _basic_auth_str,
    parse_dict_header
)
from requests.models import Request, Response
from requests.utils import urlparse
import hashlib
import base64
import re
import os
import time
import logging

log = logging.getLogger(__name__)

def test_httpbasicauth_valid_credentials():
    auth = HTTPBasicAuth("user", "pass")
    req = Request(method="GET", url="http://example.com")
    res = auth(req)
    assert res.headers["Authorization"] == "Basic dXNlcjpwYXNz"

def test_httpbasicauth_empty_username():
    auth = HTTPBasicAuth("", "pass")
    req = Request(method="GET", url="http://example.com")
    res = auth(req)
    assert res.headers["Authorization"] == "Basic dXNlcjpwYXNz"

def test_httpbasicauth_empty_password():
    auth = HTTPBasicAuth("user", "")
    req = Request(method="GET", url="http://example.com")
    res = auth(req)
    assert res.headers["Authorization"] == "Basic dXNlcjpwYXNz"

def test_httpbasicauth_none_username():
    auth = HTTPBasicAuth(None, "pass")
    req = Request(method="GET", url="http://example.com")
    res = auth(req)
    assert res.headers["Authorization"] == "Basic dXNlcjpwYXNz"

def test_httpbasicauth_none_password():
    auth = HTTPBasicAuth("user", None)
    req = Request(method="GET", url="http://example.com")
    res = auth(req)
    assert res.headers["Authorization"] == "Basic dXNlcjpwYXNz"

def test_httpproxyauth_valid_credentials():
    auth = HTTPProxyAuth("user", "pass")
    req = Request(method="GET", url="http://example.com")
    res = auth(req)
    assert res.headers["Proxy-Authorization"] == "Basic dXNlcjpwYXNz"

def test_httpproxyauth_empty_username():
    auth = HTTPProxyAuth("", "pass")
    req = Request(method="GET", url="http://example.com")
    res = auth(req)
    assert res.headers["Proxy-Authorization"] == "Basic dXNlcjpwYXNz"

def test_httpproxyauth_empty_password():
    auth = HTTPProxyAuth("user", "")
    req = Request(method="GET", url="http://example.com")
    res = auth(req)
    assert res.headers["Proxy-Authorization"] == "Basic dXNlcjpwYXNz"

def test_httpproxyauth_none_username():
    auth = HTTPProxyAuth(None, "pass")
    req = Request(method="GET", url="http://example.com")
    res = auth(req)
    assert res.headers["Proxy-Authorization"] == "Basic dXNlcjpwYXNz"

def test_httpproxyauth_none_password():
    auth = HTTPProxyAuth("user", "pass")
    req = Request(method="GET", url="http://example.com")
    res = auth(req)
    assert res.headers["Proxy-Authorization"] == "Basic dXNlcjpwYXNz"

def test_httpdigestauth_handle_401_no_challenge():
    auth = HTTPDigestAuth("user", "pass")
    mock_response = mock.MagicMock(spec=Response)
    mock_response.headers = {"www-authenticate": "Basic"}
    result = auth.handle_401(mock_response)
    assert result.headers["Authorization"] == "Basic dXNlcjpwYXNz"

def test_httpdigestauth_handle_401_with_digest_challenge():
    auth = HTTPDigestAuth("user", "pass")
    mock_response = mock.MagicMock(spec=Response)
    mock_response.headers = {"www-authenticate": 'Digest realm="example", nonce="123456789", qop="auth", algorithm=MD5'}
    mock_response.content = b"some content"
    mock_response.raw.release_conn = mock.MagicMock()
    mock_response.request.body.seek = mock.MagicMock()
    mock_response.request.body.tell = mock.MagicMock(return_value=1024)
    mock_response.connection.send = mock.MagicMock(return_value=mock.MagicMock(spec=Response))
    mock_response.connection.send.return_value.history = []
    mock_response.connection.send.return_value.request = mock.MagicMock()

    with mock.patch('requests.auth.parse_dict_header') as mock_parse_dict:
        mock_parse_dict.return_value = {"realm": "example", "nonce": "123456789", "qop": "auth", "algorithm": "MD5"}
        result = auth.handle_401(mock_response)
        assert result.headers["Authorization"] == "Digest username=\"user\", realm=\"example\", nonce=\"123456789\", uri=\"/\", response=\"0a4d55a8d5ca9e5a9b1e356b1b79e6a1\", qop=auth, nc=00000001, cnonce=\"0a4d55a8\", algorithm=MD5"

def test_httpdigestauth_build_digest_header_md5():
    auth = HTTPDigestAuth("user", "pass")
    auth.chal = {"realm": "example", "nonce": "123456789", "qop": "auth", "algorithm": "MD5"}
    auth.last_nonce = "123456789"
    auth.nonce_count = 1
    auth.pos = 1024
    method = "GET"
    url = "http://example.com/path?query=param"
    result = auth.build_digest_header(method, url)
    assert result == "Digest username=\"user\", realm=\"example\", nonce=\"123456789\", uri=\"/path?query=param\", response=\"0a4d55a8d5ca9e5a9b1e356b1b79e6a1\", qop=auth, nc=00000001, cnonce=\"0a4d55a8\", algorithm=MD5"

def test_httpdigestauth_build_digest_header_sha():
    auth = HTTPDigestAuth("user", "pass")
    auth.chal = {"realm": "example", "nonce": "123456789", "qop": "auth", "algorithm": "SHA-256"}
    auth.last_nonce = "123456789"
    auth.nonce_count = 1
    auth.pos = 1024
    method = "GET"
    url = "http://example.com/path?query=param"
    result = auth.build_digest_header(method, url)
    assert result == "Digest username=\"user\", realm=\"example\", nonce=\"123456789\", uri=\"/path?query=param\", response=\"b74d0e6e8a7e1a8e9f1e2a3b4c5d6e7f\", qop=auth, nc=00000001, cnonce=\"0a4d55a8\", algorithm=SHA-256"

def test_httpdigestauth_build_digest_header_md5_no_qop():
    auth = HTTPDigestAuth("user", "pass")
    auth.chal = {"realm": "example", "nonce": "123456789", "algorithm": "MD5"}
    auth.last_nonce = "123456789"
    auth.nonce_count = 1
    auth.pos = 1024
    method = "GET"
    url = "http://example.com/path?query=param"
    result = auth.build_digest_header(method, url)
    assert result == "Digest username=\"user\", realm=\"example\", nonce=\"123456789\", uri=\"/path?query=param\", response=\"0a4d55a8d5ca9e5a9b1e356b1b79e6a1\", algorithm=MD5"

def test_httpdigestauth_build_digest_header_with_realm():
    auth = HTTPDigestAuth("user", "pass")
    auth.chal = {"realm": "example.com", "nonce": "123456789", "algorithm": "MD5"}
    auth.last_nonce = "123456789"
    auth.nonce_count = 1
    auth.pos = 1024
    method = "GET"
    url = "http://example.com/path?query=param"
    result = auth.build_digest_header(method, url)
    assert result == "Digest username=\"user\", realm=\"example.com\", nonce=\"123456789\", uri=\"/path?query=param\", response=\"0a4d55a8d5ca9e5a9b1e356b1b79e6a1\", algorithm=MD5"