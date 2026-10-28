import unittest
import requests
from requests.sessions import Session

class TestSession(unittest.TestCase):

    def setUp(self):
        self.session = requests.Session()

    def test_get(self):
        response = self.session.get('https://httpbin.org/get')
        self.assertEqual(response.status_code, 200)

    def test_post(self):
        response = self.session.post('https://httpbin.org/post', data = {'key': 'value'})
        self.assertEqual(response.status_code, 200)

    def test_put(self):
        response = self.session.put('https://httpbin.org/put', data = {'key': 'value'})
        self.assertEqual(response.status_code, 200)

    def test_delete(self):
        response = self.session.delete('https://httpbin.org/delete')
        self.assertEqual(response.status_code, 200)

    def test_patch(self):
        response = self.session.patch('https://httpbin.org/patch', data = {'key': 'value'})
        self.assertEqual(response.status_code, 200)

    def test_head(self):
        response = self.session.head('https://httpbin.org/get')
        self.assertEqual(response.status_code, 200)

    def test_cookies(self):
        self.session.get('https://httpbin.org/cookies/set?cookie1=value1&cookie2=value2')
        cookies = self.session.cookies.get_dict()
        self.assertEqual(cookies['cookie1'], 'value1')
        self.assertEqual(cookies['cookie2'], 'value2')

    def test_session_close(self):
        self.session.close()
        self.assertEqual(self.session.is_closed, True)

    def test_session_context_manager(self):
        with requests.Session() as session:
            response = session.get('https://httpbin.org/get')
            self.assertEqual(response.status_code, 200)

if __name__ == '__main__':
    unittest.main()