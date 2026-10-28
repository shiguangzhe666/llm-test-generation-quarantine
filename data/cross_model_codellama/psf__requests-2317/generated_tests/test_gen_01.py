import unittest
from requests import Session

class TestSession(unittest.TestCase):
    def test_session(self):
        session = Session()
        self.assertIsInstance(session, Session)
        self.assertEqual(session.headers, {'User-Agent': 'python-requests'})