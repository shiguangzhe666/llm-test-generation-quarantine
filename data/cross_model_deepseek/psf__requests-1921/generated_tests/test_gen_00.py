import unittest
import requests
from requests.exceptions import InvalidSchema

class TestSession(unittest.TestCase):

    def setUp(self):
        self.s = requests.Session()

    def test_get_adapter(self):
        # Test if it raises InvalidSchema when no adapters are registered
        with self.assertRaises(InvalidSchema):
            self.s.get('https://example.com')

        # Test if it returns the correct adapter
        self.s.mount('https://', requests.adapters.HTTPAdapter())
        adapter = self.s.get_adapter('https://example.com')
        self.assertIsInstance(adapter, requests.adapters.HTTPAdapter)

    def test_close(self):
        # Test if it closes all adapters
        self.s.mount('https://', requests.adapters.HTTPAdapter())
        self.s.close()
        with self.assertRaises(InvalidSchema):
            self.s.get('https://example.com')

    def test_mount(self):
        # Test if it mounts an adapter correctly
        adapter = requests.adapters.HTTPAdapter()
        self.s.mount('https://', adapter)
        self.assertEqual(self.s.adapters['https://'], adapter)

    def test_session(self):
        # Test if session() returns a Session instance
        s = requests.session()
        self.assertIsInstance(s, requests.Session)

if __name__ == '__main__':
    unittest.main()

import unittest
import requests
from requests.exceptions import InvalidSchema

class TestSession(unittest.TestCase):

    def setUp(self):
        self.s = requests.Session()

    def test_get_adapter(self):
        # Test if it raises InvalidSchema when no adapters are registered
        with self.assertRaises(InvalidSchema):
            self.s.get('https://example.com')

        # Test if it returns the correct adapter
        self.s.mount('https://', requests.adapters.HTTPAdapter())
        adapter = self.s.get_adapter('https://example.com')
        self.assertIsInstance(adapter, requests.adapters.HTTPAdapter)

    def test_close(self):
        # Test if it closes all adapters
        self.s.mount('https://', requests.adapters.HTTPAdapter())
        self.s.close()
        with self.assertRaises(InvalidSchema):
            self.s.get('https://example.com')

    def test_mount(self):
        # Test if it mounts an adapter correctly
        adapter = requests.adapters.HTTPAdapter()
        self.s.mount('https://', adapter)
        self.assertEqual(self.s.adapters['https://'], adapter)

    def test_session(self):
        # Test if session() returns a Session instance
        s = requests.session()
        self.assertIsInstance(s, requests.Session)

if __name__ == '__main__':
    unittest.main()

import unittest
import requests
from requests.exceptions import InvalidSchema

class TestSession(unittest.TestCase):

    def setUp(self):
        self.s = requests.Session()

    def test_get_adapter(self):
        # Test if it raises InvalidSchema when no adapters are registered
        with self.assertRaises(InvalidSchema):
            self.s.get('https://example.com')

        # Test if it returns the correct adapter
        self.s.mount('https://', requests.adapters.HTTPAdapter())
        adapter = self.s.get_adapter('https://example.com')
        self.assertIsInstance(adapter, requests.adapters.HTTPAdapter)

    def test_close(self):
        # Test if it closes all adapters
        self.s.mount('https://', requests.adapters.HTTPAdapter())
        self.s.close()
        with self.assertRaises(InvalidSchema):
            self.s.get('https://example.com')

    def test_mount(self):
        # Test if it mounts an adapter correctly
        adapter = requests.adapters.HTTPAdapter()
        self.s.mount('https://', adapter)
        self.assertEqual(self.s.adapters['https://'], adapter)

    def test_session(self):
        # Test if session() returns a Session instance
        s = requests.session()
        self.assertIsInstance(s, requests.Session)

if __name__ == '__main__':
    unittest.main()

import unittest
import requests
from requests.exceptions import InvalidSchema

class TestSession(unittest.TestCase):

    def setUp(self):
        self.s = requests.Session()

    def test_get_adapter(self):
        # Test if it raises InvalidSchema when no adapters are registered
        with self.assertRaises(InvalidSchema):
            self.s.get('https://example.com')

        # Test if it returns the correct adapter
        self.s.mount('https://', requests.adapters.HTTPAdapter())
        adapter = self.s.get_adapter('https://example.com')
        self.assertIsInstance(adapter, requests.adapters.HTTPAdapter)

    def test_close(self):
        # Test if it closes all adapters
        self.s.mount('https://', requests.adapters.HTTPAdapter())
        self.s.close()
        with self.assertRaises(InvalidSchema):
            self.s.get('https://example.com')

    def test_mount(self):
        # Test if it mounts an adapter correctly
        adapter = requests.adapters.HTTPAdapter()
        self.s.mount('https://', adapter)
        self.assertEqual(self.s.adapters['https://'], adapter)

    def test_session(self):
        # Test if session() returns a Session instance
        s = requests.session()
        self.assertIsInstance(s, requests.Session)

if __name__ == '__main__':
    unittest.main()

import unittest
import requests
from requests.exceptions import InvalidSchema

class TestSession(unittest.TestCase):

    def setUp(self):
        self.s = requests.Session()

    def test_get_adapter(self):
        # Test if it raises InvalidSchema when no adapters are registered
        with self.assertRaises(InvalidSchema):
            self.s.get('https://example.com')

        # Test if it returns the correct adapter
        self.s.mount('https://', requests.adapters.HTTPAdapter())
        adapter = self.s.get_adapter('https://example.com')
        self.assertIsInstance(adapter, requests.adapters.HTTPAdapter)

    def test_close(self):
        # Test if it closes all adapters
        self.s.mount('https://', requests.adapters.HTTPAdapter())
        self.s.close()
        with self.assertRaises(InvalidSchema):
            self.s.get('https://example.com')

    def test_mount(self):
        # Test if it mounts an adapter correctly
        adapter = requests.adapters.HTTPAdapter()
        self.s.mount('https://', adapter)
        self.assertEqual(self.s.adapters['https://'], adapter)

    def test_session(self):
        # Test if session() returns a Session instance
        s = requests.session()
        self.assertIsInstance(s, requests.Session)

if __name__ == '__main__':
    unittest.main()

import unittest
import requests
from requests.exceptions import InvalidSchema

class TestSession(unittest.TestCase):

    def setUp(self):
        self.s = requests.Session()

    def test_get_adapter(self):
        # Test if it raises InvalidSchema when no adapters are registered
        with self.assertRaises(InvalidSchema):
            self.s.get('https://example.com')

        # Test if it returns the correct adapter
        self.s.mount('https://', requests.adapters.HTTPAdapter())
        adapter = self.s.get_adapter('https://example.com')
        self.assertIsInstance(adapter, requests.adapters.HTTPAdapter)

    def test_close(self):
        # Test if it closes all adapters
        self.s.mount('https://', requests.adapters.HTTPAdapter())
        self.s.close()
        with self.assertRaises(InvalidSchema):
            self.s.get('https://example.com')

    def test_mount(self):
        # Test if it mounts an adapter correctly
        adapter = requests.adapters.HTTPAdapter()
        self.s.mount('https://', adapter)
        self.assertEqual(self.s.adapters['https://'], adapter)

    def test_session(self):
        # Test if session() returns a Session instance
        s = requests.session()
        self.assertIsInstance(s, requests.Session)

if __name__ == '__main__':
    unittest.main()