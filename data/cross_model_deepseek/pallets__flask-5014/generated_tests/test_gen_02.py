import unittest
from flask import Flask
from your_blueprint_file import YourBlueprint

class TestYourBlueprint(unittest.TestCase):
    def setUp(self):
        self.app = Flask(__name__)
        self.bp = YourBlueprint()
        self.bp.init_app(self.app)
        self.client = self.app.test_client()

    def test_home_page(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)

    def test_about_page(self):
        response = self.client.get('/about')
        self.assertEqual(response.status_code, 200)

    def test_app_template_filter(self):
        response = self.client.get('/template_filter_test')
        self.assertEqual(response.status_code, 200)
        self.assertIn('This is a test string', response.data.decode())

    def test_app_template_test(self):
        response = self.client.get('/template_test_test')
        self.assertEqual(response.status_code, 200)
        self.assertIn('Test is True', response.data.decode())

    def test_app_template_global(self):
        response = self.client.get('/template_global_test')
        self.assertEqual(response.status_code, 200)
        self.assertIn('Global Test', response.data.decode())

    def test_before_app_request(self):
        response = self.client.get('/before_request_test')
        self.assertEqual(response.status_code, 200)
        self.assertIn('Before Request Test', response.data.decode())

    def test_after_app_request(self):
        response = self.client.get('/after_request_test')
        self.assertEqual(response.status_code, 200)
        self.assertIn('After Request Test', response.data.decode())

    def test_teardown_app_request(self):
        response = self.client.get('/teardown_request_test')
        self.assertEqual(response.status_code, 200)
        self.assertIn('Teardown Request Test', response.data.decode())

    def test_app_errorhandler(self):
        response = self.client.get('/404')
        self.assertEqual(response.status_code, 404)
        self.assertIn('404 Error', response.data.decode())

if __name__ == '__main__':
    unittest.main()