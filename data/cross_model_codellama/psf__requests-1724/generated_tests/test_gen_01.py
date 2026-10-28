import unittest

from requests import Session


class SessionTest(unittest.TestCase):
    def test_session(self):
        with Session() as session:
            self.assertIsNotNone(session)


if __name__ == '__main__':
    unittest.main()