import unittest
from requests import session

class TestSession(unittest.TestCase):
    def test_session(self):
        with session() as c:
            self.assertIsInstance(c, session)