import unittest
from requests import Session, Request

class TestSession(unittest.TestCase):

    def setUp(self):
        self.session = Session()

    def test_get(self):
        response = self.session.get('http://httpbin.org/get')
        self.assertEqual(response.status_code, 200)

    def test_post(self):
        response = self.session.post('http://httpbin.org/post', data={'key': 'value'})
        self.assertEqual(response.status_code, 200)

    def test_put(self):
        response = self.session.put('http://httpbin.org/put', data={'key': 'value'})
        self.assertEqual(response.status_code, 200)

    def test_patch(self):
        response = self.session.patch('http://httpbin.org/patch', data={'key': 'value'})
        self.assertEqual(response.status_code, 200)

    def test_delete(self):
        response = self.session.delete('http://httpbin.org/delete')
        self.assertEqual(response.status_code, 200)

    def test_head(self):
        response = self.session.head('http://httpbin.org/get')
        self.assertEqual(response.status_code, 200)

    def test_options(self):
        response = self.session.options('http://httpbin.org/get')
        self.assertEqual(response.status_code, 200)

    def test_send(self):
        request = Request('GET', 'http://httpbin.org/get')
        response = self.session.send(request.prepare())
        self.assertEqual(response.status_code, 200)

if __name__ == '__main__':
    unittest.main()