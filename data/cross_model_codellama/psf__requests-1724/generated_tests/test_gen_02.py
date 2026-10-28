import unittest

class TestSession(unittest.TestCase):

    def test_session(self):
        session = session()
        self.assertIsInstance(session, Session)
        self.assertTrue(hasattr(session, 'get'))
        self.assertTrue(hasattr(session, 'post'))
        self.assertTrue(hasattr(session, 'put'))
        self.assertTrue(hasattr(session, 'patch'))
        self.assertTrue(hasattr(session, 'delete'))
        self.assertTrue(hasattr(session, 'head'))
        self.assertTrue(hasattr(session, 'options'))
        self.assertTrue(hasattr(session, 'close'))
        self.assertTrue(hasattr(session, 'mount'))
        self.assertTrue(hasattr(session, 'adapters'))
        self.assertTrue(hasattr(session, 'cookies'))
        self.assertTrue(hasattr(session, 'hooks'))
        self.assertTrue(hasattr(session, 'send'))
        self.assertTrue(hasattr(session, 'resolve_redirects'))
        self.assertTrue(hasattr(session, 'get_adapter'))


if __name__ == '__main__':
    unittest.main()