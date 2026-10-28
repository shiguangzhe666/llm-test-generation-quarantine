import pytest
import unittest
from unittest.mock import patch, MagicMock, Mock
from requests.auth import (
    AuthBase, HTTPBasicAuth, HTTPProxyAuth, HTTPDigestAuth,
    _basic_auth_str, parse_dict_header
)
from requests.models import Response
from requests import Request, Session
from requests.utils import parse_dict_header
from urllib.parse import urlparse
import hashlib
import base64
import re
import time
import os
import logging

logging.getLogger('requests').setLevel(logging.CRITICAL)

@pytest.fixture
def auth_base():
    with pytest.raises(NotImplementedError):
        AuthBase()

@pytest.fixture
def http_basic_auth():
    auth = HTTPBasicAuth('user', 'pass')
    return auth

@pytest.fixture
def http_proxy_auth():
    auth = HTTPProxyAuth('user', 'pass')
    return auth

@pytest.fixture
def http_digest_auth():
    auth = HTTPDigestAuth('user', 'pass')
    return auth

def test_basic_auth_str():
    assert _basic_auth_str('user', 'pass') == 'Basic dXNlcjpwYXNz'
    assert _basic_auth_str('', '') == 'Basic ' + base64.b64encode(b'').decode('latin1')
    assert _basic_auth_str('user', '') == 'Basic dXNlcw=='
    assert _basic_auth_str('', 'pass') == 'Basic cGFzcw=='
    assert _basic_auth_str('u', 'p') == 'Basic dVw='
    assert _basic_auth_str('u', 'p') == 'Basic dVw='
    assert _basic_auth_str('u', 'p') == 'Basic dVw='
    assert _basic_auth_str('u', 'p') == 'Basic dVw='
    assert _basic_auth_str('u', 'p') == 'Basic dVw='
    assert _basic_auth_str('u', 'p') == 'Basic dVw='
    assert _basic_auth_str('u', 'p') == 'Basic dVw='
    assert _basic_auth_str('u', 'p') == 'Basic dVw='
    assert _basic_auth_str('u', 'p') == 'Basic dVw='
    assert _basic_auth_str('u', 'p') == 'Basic dVw='

def test_http_basic_auth(http_basic_auth):
    req = Request('GET', 'http://example.com')
    res = http_basic_auth(req)
    assert res.headers['Authorization'] == 'Basic dXNlcjpwYXNz'

def test_http_proxy_auth(http_proxy_auth):
    req = Request('GET', 'http://example.com')
    res = http_proxy_auth(req)
    assert res.headers['Proxy-Authorization'] == 'Basic dXNlcjpwYXNz'

def test_http_digest_auth_build_digest_header(http_digest_auth):
    with patch('requests.auth.parse_dict_header') as mock_parse_dict_header:
        mock_parse_dict_header.return_value = {'realm': 'realm', 'nonce': 'nonce', 'qop': 'auth', 'algorithm': 'MD5'}
        digest_header = http_digest_auth.build_digest_header('GET', 'http://example.com')
        assert digest_header.startswith('Digest username="user", realm="realm", nonce="nonce", uri="/example.com", ')
        assert 'response' in digest_header
        assert 'qop=auth' in digest_header

def test_http_digest_auth_handle_401(http_digest_auth):
    mock_response = MagicMock(spec=Response)
    mock_response.status_code = 401
    mock_response.headers = {'www-authenticate': 'Digest realm="test", nonce="1234567890", qop="auth", algorithm=MD5'}
    mock_response.content = b''

    with patch('requests.models.Response.content', new_callable=property) as mock_content:
        mock_content.return_value = b''

    with patch('requests.models.Response.raw.release_conn') as mock_release_conn:
        with patch('requests.models.Response.request') as mock_request:
            with patch('requests.models.Response.connection.send') as mock_send:
                with patch('requests.models.Response.history', new_callable=list):
                    mock_response = MagicMock(spec=Response)
                    mock_response.status_code = 401
                    mock_response.headers = {'www-authenticate': 'Digest realm="test", nonce="1234567890", qop="auth", algorithm=MD5'}
                    mock_response.content = b''

                    res = http_digest_auth.handle_401(mock_response)
                    assert res.status_code == 200
                    assert 'Authorization' in res.request.headers
                    assert res.request.headers['Authorization'].startswith('Digest username="user", realm="test", nonce="1234567890", uri="http://example.com", ')

def test_http_digest_auth_build_digest_header_with_sha_algorithm(http_digest_auth):
    with patch('requests.auth.parse_dict_header') as mock_parse_dict_header:
        mock_parse_dict_header.return_value = {'realm': 'realm', 'nonce': 'nonce', 'qop': 'auth', 'algorithm': 'SHA'}
        digest_header = http_digest_auth.build_digest_header('GET', 'http://example.com')
        assert digest_header.startswith('Digest username="user", realm="realm", nonce="nonce", uri="/example.com", ')
        assert 'algorithm="SHA"' in digest_header

def test_http_digest_auth_build_digest_header_with_missing_opaque(http_digest_auth):
    with patch('requests.auth.parse_dict_header') as mock_parse_dict_header:
        mock_parse_dict, mock_parse_dict_header.return_value = {'realm': 'realm', 'nonce': 'nonce', 'qop': 'auth', 'algorithm': 'MD5'}
        digest_header = http_digest_auth.build_digest_header('GET', 'http://example.com')
        assert 'opaque' not in digest_header

def test_http_digest_auth_build_digest_header_with_stale_nonce(http_digest_auth):
    with patch('requests.auth.parse_dict_header') as mock_parse_dict_header:
        mock_parse_dict_header.return_value = {'realm': 'realm', 'nonce': 'nonce', 'stale': 'true', 'qop': 'auth', 'algorithm': 'MD5'}
        digest_header = http_digest_auth.build_digest_header('GET', 'http://example.com')
        assert 'stale' in digest_header
        assert 'stale=true' in digest_header

def test_http_digest_auth_build_digest_header_with_multiple_qop_values(http_digest_auth):
    with patch('requests.auth.parse_dict_header') as mock_parse_dict_header:
        mock_parse_dict_header.return_value = {'realm': 'realm', 'nonce': 'nonce', 'qop': 'auth, exp', 'algorithm': 'MD5'}
        digest_header = http_digest_auth.build_digest_header('GET', 'http://example.com')
        assert 'qop=auth, exp' in digest_header

def test_http_digest_auth_build_digest_header_with_algorithm_md5(http_digest_auth):
    with patch('requests.auth.parse_dict_header') as mock_parse_dict_header:
        mock_parse_dict_header.return_value = {'realm': 'realm', 'nonce': 'nonce', 'qop': 'auth', 'algorithm': 'MD5'}
        digest_header = http_digest_auth.build_digest_header('GET', 'http://example.com')
        assert 'algorithm="MD5"' in digest_header

def test_http_digest_auth_build_digest_header_with_algorithm_sha(http_digest_auth):
    with patch('requests.auth.parse_dict_header') as mock_parse_dict_header:
        mock_parse_dict_header.return_value = {'realm': 'realm', 'nonce': 'nonce', 'qop': 'auth', 'algorithm': 'SHA'}
        digest_header = http_digest_auth.build_digest_header('GET', 'http://example.com')
        assert 'algorithm="SHA"' in digest_header

def test_http_digest_auth_build_digest_header_with_invalid_algorithm(http_digest_auth):
    with patch('requests.auth.parse_dict_header') as mock_parse_dict_header:
        mock_parse_dict_header.return_value = {'realm': 'realm', 'nonce': 'nonce', 'qop': 'auth', 'algorithm': 'invalid'}
        digest_header = http_digest_auth.build_digest_header('GET', 'http://example.com')
        assert 'algorithm="invalid"' in digest_header

def test_http_digest_auth_build_digest_header_with_missing_qop(http_digest_auth):
    with patch('requests.auth.parse_dict_header') as mock_parse_dict_header:
        mock_parse_dict_header.return_value = {'realm': 'realm', 'nonce': 'nonce', 'algorithm': 'MD5'}
        digest_header = http_digest_auth.build_digest_header('GET', 'http://example.com')
        assert 'qop' not in digest_header

def test_http_digest_auth_build_digest_header_with_missing_realm(http_digest_auth):
    with patch('requests.auth.parse_dict_header') as mock_parse_dict_header:
        mock_parse_dict_header.return_value = {'nonce': 'nonce', 'qop': 'auth', 'algorithm': 'MD5'}
        digest_header = http_digest_auth.build_digest_header('GET', 'http://example.com')
        assert 'realm' not in digest_header

def test_http_digest_auth_build_digest_header_with_missing_nonce(http_digest_auth):
    with patch('requests.auth.parse_dict_header') as mock_parse_dict_header:
        mock_parse_dict_header.return_value = {'realm': 'realm', 'qop': 'auth', 'algorithm': 'MD5'}
        digest_header = http_digest_auth.build_digest_header('GET', 'http://example.com')
        assert 'nonce' not in digest_header

def test_http_digest_auth_build_digest_header_with_missing_algorithm(http_digest_auth):
    with patch('requests.auth.parse_dict_header') as mock_parse_dict_header:
        mock_parse_dict_header.return_value = {'realm': 'realm', 'nonce': 'nonce', 'qop': 'auth'}
        digest_header = http_digest_auth.build_digest_header('GET', 'http://example.com')
        assert 'algorithm' not in digest_header

def test_http_digest_auth_build_digest_header_with_missing_uri(http_digest_auth):
    with patch('requests.auth.parse_dict_header') as mock_parse_dict_header:
        mock_parse_dict_header.return_value = {'realm': 'realm', 'nonce': 'nonce', 'qop': 'auth', 'algorithm': 'MD5'}
        digest_header = http_digest_auth.build_digest_header('GET', 'http://example.com')
        assert 'uri' in digest_header
        assert 'uri="/example.com"' in digest_header

def test_http_digest_auth_build_digest_header_with_custom_uri(http_digest_auth):
    with patch('requests.auth.parse_dict_header') as mock_parse_dict_header:
        mock_parse_dict_header.return_value = {'realm': 'realm', 'nonce': 'nonce', 'qop': 'auth', 'algorithm': 'MD5'}
        digest_header = http_digest_auth.build_digest_header('GET', 'http://example.com/path?query=123')
        assert 'uri="/example.com/path?query=123"' in digest_header

def test_http_digest_auth_build_digest_header_with_special_characters(http_digest_auth):
    with patch('requests.auth.parse_dict_header') as mock_parse_dict_header:
        mock_parse_dict_header.return_value = {'realm': 'realm', 'nonce': 'nonce', 'qop': 'auth', 'algorithm': 'MD5'}
        digest_header = http_digest_auth.build_digest_header('GET', 'http://example.com/path?query=123')
        assert 'uri="/example.com/path?query=123"' in digest_header