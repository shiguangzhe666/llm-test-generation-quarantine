import os
import requests
from requests.structures import CaseInsensitiveDict
from requests.models import Response, PreparedRequest, Request, Session, merge_setting, dispatch_hook, get_environ_proxies

def test_session_context_manager():
    with requests.session() as session:
        response = session.get('https://httpbin.org/get')
        assert response.status_code == 200

def test_request_method():
    session = requests.Session()
    response = session.request('GET', 'https://httpbin.org/get')
    assert response.status_code == 200

def test_get_method():
    response = requests.get('https://httpbin.org/get')
    assert response.status_code == 200

def test_options_method():
    response = requests.options('https://httpbin.org/anything')
    assert response.status_code == 200

def test_head_method():
    response = requests.head('https://httpbin.org/get')
    assert response.status_code == 200

def test_post_method():
    response = requests.post('https://httpbin.org/post', data={'key': 'value'})
    assert response.status_code == 200

def test_put_method():
    response = requests.put('https://httpbin.org/put', data={'key': 'value'})
    assert response.status_code == 200

def test_patch_method():
    response = requests.patch('https://httpbin.org/patch', data={'key': 'value'})
    assert response.status_code == 200

def test_delete_method():
    response = requests.delete('https://httpbin.org/delete')
    assert response.status_code == 200

def test_send_method():
    session = requests.Session()
    response = session.send(session.prepare_request(Request('GET', 'https://httpbin.org/get')))
    assert response.status_code == 200

def test_adapter_registration():
    class MockAdapter:
        def send(self, request, **kwargs):
            return Response(200, request.url)

    session = requests.Session()
    session.mount('https://httpbin.org/', MockAdapter())
    response = session.get('https://httpbin.org/get')
    assert response.status_code == 200

def test_context_close():
    session = requests.Session()
    session.get('https://httpbin.org/get')
    session.close()
    try:
        session.get('https://httpbin.org/get')
    except requests.exceptions_closed_session:
        pass
    else:
        assert False, "Session should be closed"

def test_session_cookies():
    session = requests.Session()
    session.cookies.set('key', 'value')
    response = session.get('https://httpbin.org/cookies')
    assert response.json()['cookies']['key'] == 'value'