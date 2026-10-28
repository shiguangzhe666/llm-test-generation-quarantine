import os
import datetime
from requests.packages.urllib3.response import HTTPResponse
from requests.packages.urllib3.exceptions import InsecureRequestWarning
from requests.packages.urllib3.poolmanager import PoolManager,ProxyManager,NSProxyManager
from requests.packages.urllib3.util.retry import Retry
from requests.packages.urllib3.util.ssl_ import create_urllib3_context
from requests.models import Request, Response, PreparedRequest, Session
from requests.compat import builtin_str
from requests.auth import HTTPProxyAuth
from requests.hooks import dispatch_hook
from requests.adapters import HTTPAdapter, DEFAULT_POOL_TIMEOUT, DEFAULT_RETRIES
from requests.utils import get_environ_proxies, merge_setting

class TestSession:
    def setup_method(self):
        self.session = Session()
        self.base_url = 'http://httpbin.org/'

    def teardown_method(self):
        self.session.close()

    def test_session(self):
        response = self.session.get(self.base_url + 'get')
        assert response.status_code == 200

    def test_post(self):
        data = {'key': 'value'}
        response = self.session.post(self.base_url + 'post', data=data)
        assert response.status_code == 200
        assert response.json()['form'] == data

    def test_custom_headers(self):
        headers = {'X-Custom-Header': 'Token'}
        response = self.session.get(self.base_url + 'headers', headers=headers)
        assert response.status_code == 200
        assert response.json()['headers']['X-Custom-Header'] == 'Token'

    def test_proxies(self):
        proxies = {'http': 'http://user:pass@proxy.com:3128', 'https': 'https://user:pass@proxy.com:3128'}
        response = self.session.get(self.base_url + 'get', proxies=proxies)
        assert response.status_code == 200

    def test_timeout(self):
        response = self.session.get(self.base_url + 'delay/5', timeout=3)
        assert response.status_code == 200

    def test_auth(self):
        auth = HTTPProxyAuth('user', 'pass')
        response = self.session.get(self.base_url + 'proxy-auth', proxies={'http': 'http://localhost:3128'}, auth=auth)
        assert response.status_code == 200

    def test_session_cookies(self):
        response = self.session.get(self.base_url + 'cookies/set?name=foo&value=bar')
        assert response.status_code == 200
        response = self.session.get(self.base_url + 'cookies')
        assert response.status_code == 200
        assert response.json()['cookies']['foo'] == 'bar'

    def test_session_context(self):
        with Session() as s:
            response = s.get(self.base_url + 'get')
            assert response.status_code == 200

    def test_send_request(self):
        req = Request('GET', self.base_url + 'get')
        prepped = self.session.prepare_request(req)
        response = self.session.send(prepped)
        assert response.status_code == 200

    def test_session_close(self):
        self.session.close()
        assert self.session.adapters == {}