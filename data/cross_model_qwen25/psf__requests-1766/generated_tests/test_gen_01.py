import pytest
from requests.auth import HTTPBasicAuth, HTTPProxyAuth, HTTPDigestAuth
from requests.models import Request, Response
from requests.structures import CaseInsensitiveDict
from unittest.mock import patch, MagicMock
from base64 import b64encode
import hashlib
from io import BytesIO

def test_http_basic_auth():
    auth = HTTPBasicAuth('user', 'pass')
    req = Request('GET', 'http://example.com')
    prep = req.prepare()
    auth(prep)
    assert prep.headers['Authorization'] == 'Basic dXNlcjpwYXNz'

def test_http_proxy_auth():
    auth = HTTPProxyAuth('user', 'pass')
    req = Request('GET', 'http://example.com')
    prep = req.prepare()
    auth(prep)
    assert prep.headers['Proxy-Authorization'] == 'Basic dXNlcjpwYXNz'

def test_http_digest_auth():
    auth = HTTPDigestAuth('user', 'pass')
    req = Request('GET', 'http://example.com')
    prep = req.prepare()
    auth(prep)
    assert 'Authorization' in prep.headers

def test_http_digest_auth_401_handling():
    auth = HTTPDigestAuth('user', 'pass')
    resp = Response()
    resp.status_code = 401
    resp.headers['www-authenticate'] = 'Digest realm="realm", nonce="nonce", qop=auth'
    req = Request('GET', 'http://example.com')
    prep = req.prepare()
    prep.body = BytesIO(b'body')
    prep.prepare_cookies = MagicMock()
    prep.prepare_body = MagicMock(return_value=(b'body', {}))
    prep.prepare_headers = MagicMock(return_value=CaseInsensitiveDict())
    auth(prep)
    assert prep.headers['Authorization']
    resp.content = b'content'
    prep.body.seek(0)
    prep.prepare_body = MagicMock(return_value=(b'body', {}))
    resp = auth.handle_401(resp, request=prep)
    assert resp.status_code == 200

def test_http_digest_auth_401_handling_no_nonce():
    auth = HTTPDigestAuth('user', 'pass')
    resp = Response()
    resp.status_code = 401
    resp.headers['www-authenticate'] = 'Digest realm="realm"'
    req = Request('GET', 'http://example.com')
    prep = req.prepare()
    prep.body = BytesIO(b'body')
    prep.prepare_cookies = MagicMock()
    prep.prepare_body = MagicMock(return_value=(b'body', {}))
    prep.prepare_headers = MagicMock(return_value=CaseInsensitiveDict())
    auth(prep)
    assert prep.headers['Authorization']
    resp.content = b'content'
    prep.body.seek(0)
    prep.prepare_body = MagicMock(return_value=(b'body', {}))
    resp = auth.handle_401(resp, request=prep)
    assert resp.status_code == 200

def test_http_digest_auth_401_handling_no_qop():
    auth = HTTPDigestAuth('user', 'pass')
    resp = Response()
    resp.status_code = 401
    resp.headers['www-authenticate'] = 'Digest realm="realm", nonce="nonce"'
    req = Request('GET', 'http://example.com')
    prep = req.prepare()
    prep.body = BytesIO(b'body')
    prep.prepare_cookies = MagicMock()
    prep.prepare_body = MagicMock(return_value=(b'body', {}))
    prep.prepare_headers = MagicMock(return_value=CaseInsensitiveDict())
    auth(prep)
    assert prep.headers['Authorization']
    resp.content = b'content'
    prep.body.seek(0)
    prep.prepare_body = MagicMock(return_value=(b'body', {}))
    resp = auth.handle_401(resp, request=prep)
    assert resp.status_code == 200

def test_http_digest_auth_qop_auth():
    auth = HTTPDigestAuth('user', 'pass')
    resp = Response()
    resp.status_code = 401
    resp.headers['www-authenticate'] = 'Digest realm="realm", nonce="nonce", qop=auth'
    req = Request('GET', 'http://example.com')
    prep = req.prepare()
    prep.body = BytesIO(b'body')
    prep.prepare_cookies = MagicMock()
    prep.prepare_body = MagicMock(return_value=(b'body', {}))
    prep.prepare_headers = MagicMock(return_value=CaseInsensitiveDict())
    auth(prep)
    assert prep.headers['Authorization']
    resp.content = b'content'
    prep.body.seek(0)
    prep.prepare_body = MagicMock(return_value=(b'body', {}))
    resp = auth.handle_401(resp, request=prep)
    assert resp.status_code == 200