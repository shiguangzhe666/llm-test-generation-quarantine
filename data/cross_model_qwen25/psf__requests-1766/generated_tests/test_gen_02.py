import pytest
from requests.auth import HTTPBasicAuth, HTTPProxyAuth, HTTPDigestAuth
from requests.models import PreparedRequest
from unittest.mock import patch, Mock

def test_http_basic_auth():
    auth = HTTPBasicAuth('user', 'pass')
    prepared_request = PreparedRequest()
    prepared_request.headers = {}
    prepared_request.prepare_url = Mock(return_value='http://example.com')
    prepared_request.prepare_body = Mock(return_value=None)
    auth(prepared_request)
    assert prepared_request.headers['Authorization'] == 'Basic dXNlcjptaGQ='

def test_http_proxy_auth():
    auth = HTTPProxyAuth('user', 'pass')
    prepared_request = PreparedRequest()
    prepared_request.headers = {}
    prepared_request.prepare_url = Mock(return_value='http://example.com')
    prepared_request.prepare_body = Mock(return_value=None)
    auth(prepared_request)
    assert prepared_request.headers['Proxy-Authorization'] == 'Basic dXNlcjptaGQ='

def test_http_digest_auth():
    auth = HTTPDigestAuth('user', 'pass')
    prepared_request = PreparedRequest()
    prepared_request.headers = {}
    prepared_request.prepare_url = Mock(return_value='http://example.com')
    prepared_request.prepare_body = Mock(return_value=None)
    auth(prepared_request)
    assert 'Authorization' in prepared_request.headers
    assert 'num_401_calls' in auth.__dict__ and auth.num_401_calls == 1

def test_http_digest_auth_handle_401():
    auth = HTTPDigestAuth('user', 'pass')
    response = Mock()
    response.request = PreparedRequest()
    response.request.prepare_url = Mock(return_value='http://example.com')
    response.request.prepare_body = Mock(return_value=None)
    response.request.body = Mock()
    response.request.body.tell = Mock(return_value=0)
    response.request.body.seek = Mock()
    response.history = []
    response.request.headers = {}
    response.request.register_hook = Mock()
    response.headers = {'www-authenticate': 'Digest realm="Test Realm", nonce="test_nonce", algorithm="MD5"'}
    response.content = b''
    response.raw.release_conn = Mock()
    response.connection.send = Mock(return_value=response)
    response.connection = Mock()
    auth.handle_401(response)
    assert 'Authorization' in response.request.headers
    assert response.request.register_hook.call_count == 1
    assert response.request.register_hook.call_args[0][0] == 'response'

def test_http_digest_auth_handle_401_no_nonce():
    auth = HTTPDigestAuth('user', 'pass')
    response = Mock()
    response.request = PreparedRequest()
    response.request.prepare_url = Mock(return_value='http://example.com')
    response.request.prepare_body = Mock(return_value=None)
    response.request.body = Mock()
    response.request.body.tell = Mock(return_value=0)
    response.request.body.seek = Mock()
    response.request.headers = {}
    response.headers = {'www-authenticate': 'Digest realm="Test Realm", nonce=""'}
    response.content = b''
    response.raw.release_conn = Mock()
    response.connection.send = Mock(return_value=response)
    response.connection = Mock()
    auth.handle_401(response)
    assert 'Authorization' in response.request.headers
    assert 'num_401_calls' in auth.__dict__ and auth.num_401_calls == 2