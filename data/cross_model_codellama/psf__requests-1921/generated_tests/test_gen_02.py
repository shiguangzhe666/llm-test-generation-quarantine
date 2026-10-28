import unittest

class TestSession(unittest.TestCase):
    def test_session(self):
        self.assertEqual(session(), Session())

if __name__ == '__main__':
    unittest.main()