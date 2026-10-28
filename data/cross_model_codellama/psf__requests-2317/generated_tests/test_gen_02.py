import unittest
from requests import Session


class TestSession(unittest.TestCase):

    def test_session(self):
        with Session() as session:
            self.assertIsInstance(session, Session)


if __name__ == '__main__':
    unittest.main()