import requests
import unittest
from unittest.mock import Mock, patch

class TestSession(unittest.TestCase):

    @patch('requests.Session.send')
    def test_send(self, mock_send):
        s = requests.Session()
        mock_send.return_value = Mock()
        mock_send.return_value.status_code = 200
        r = s.get('http://www.google.com')
        self.assertEqual(r.status_code, 200)

    @patch('requests.Session.get')
    def test_get(self, mock_get):
        s = requests.Session()
        mock_get.return_value = Mock()
        mock_get.return_value.status_code = 200
        r = s.get('http://www.google.com')
        self.assertEqual(r.status_code, 200)

    @patch('requests.Session.options')
    def test_options(self, mock_options):
        s = requests.Session()
        mock_options.return_value = Mock()
        mock_options.returncode = 200
        r = s.options('http://www.google.com')
        self.assertEqual(r.status_code, 200)

    @patch('requests.Session.head')
    def test_head(self, mock_head):
        s = requests.Session()
        mock_head.return_value = Mock()
        mock_head.return_value.status_code = 200
        r = s.head('http://www.google.com')
        self.assertEqual(r.status_code, 200)

    @patch('requests.Session.post')
    def test_post(self, mock_post):
        s = requests.Session()
        mock_post.return_value = Mock()
        mock_post.return_value.status_code = 200
        r = s.post('http://www.google.com')
        self.assertEqual(r.status_code, 200)

    @patch('requests.Session.put')
    def test_put(self, mock_put):
        s = requests.Session()
        mock_put.return_value = Mock()
        mock_put.return_value.status_code = 200
        r = s.put('http://www.google.com')
        self.assertEqual(r.status_code, 200)

    @patch('requests.Session.patch')
    def test_patch(self, mock_patch):
        s = requests.Session()
        mock_patch.return_value = Mock()
        mock_patch.return_value.status_code = 200
        r = s.patch('http://www.google.com')
        self.assertEqual(r.status_code, 200)

    @patch('requests.Session.delete')
    def test_delete(self, mock_delete):
        s = requests.Session()
        mock_delete.return_value = Mock()
        mock_delete.return_value.status_code = 200
        r = s.delete('http://www.google.com')
        self.assertEqual(r.status_code, 200)

    @patch('requests.Session.close')
    def test_close(self, mock_close):
        s = requests.Session()
        mock_close.return_value = Mock()
        s.close()
        mock_close.assert_called_once()

if __name__ == '__main__':
    unittest.main()

import requests
import unittest
from unittest.mock import Mock, patch

class TestSession(unittest.TestCase):

    @patch('requests.Session.send')
    def test_send(self, mock_send):
        s = requests.Session()
        mock_send.return_value = Mock()
        mock_send.return_value.status_code = 200
        r = s.get('http://www.google.com')
        self.assertEqual(r.status_code, 200)

    @patch('requests.Session.get')
    def test_get(self, mock_get):
        s = requests.Session()
        mock_get.return_value = Mock()
        mock_get.return_value.status_code = 200
        r = s.get('http://www.google.com')
        self.assertEqual(r.status_code, 200)

    @patch('requests.Session.options')
    def test_options(self, mock_options):
        s = requests.Session()
        mock_options.return_value = Mock()
        mock_options.return_value.status_code = 200
        r = s.options('http://www.google.com')
        self.assertEqual(r.status_code, 200)

    @patch('requests.Session.head')
    def test_head(self, mock_head):
        s = requests.Session()
        mock_head.return_value = Mock()
        mock_head.return_value.status_code = 200
        r = s.head('http://www.google.com')
        self.assertEqual(r.status_code, 200)

    @patch('requests.Session.post')
    def test_post(self, mock_post):
        s = requests.Session()
        mock_post.return_value = Mock()
        mock_post.return_value.status_code = 200
        r = s.post('http://www.google.com')
        self.assertEqual(r.status_code, 200)

    @patch('requests.Session.put')
    def test_put(self, mock_put):
        s = requests.Session()
        mock_put.return_value = Mock()
        mock_put.return_value.status_code = 200
        r = s.put('http://www.google.com')
        self.assertEqual(r.status_code, 200)

    @patch('requests.Session.patch')
    def test_patch(self, mock_patch):
        s = requests.Session()
        mock_patch.return_value = Mock()
        mock_patch.return_value.status_code = 200
        r = s.patch('http://www.google.com')
        self.assertEqual(r.status_code, 200)

    @patch('requests.Session.delete')
    def test_delete(self, mock_delete):
        s = requests.Session()
        mock_delete.return_value = Mock()
        mock_delete.return_value.status_code = 200
        r = s.delete('http://www.google.com')
        self.assertEqual(r.status_code, 200)

    @patch('requests.Session.close')
    def test_close(self, mock_close):
        s = requests.Session()
        mock_close.return_value = Mock()
        s.close()
        mock_close.assert_called_once()

if __name__ == '__main__':
    unittest.main()

import requests
import unittest
from unittest.mock import Mock, patch

class TestSession(unittest.TestCase):

    @patch('requests.Session.send')
    def test_send(self, mock_send):
        s = requests.Session()
        mock_send.return_value = Mock()
        mock_send.return_value.status_code = 200
        r = s.get('http://www.google.com')
        self.assertEqual(r.status_code, 200)

    @patch('requests.Session.get')
    def test_get(self, mock_get):
        s = requests.Session()
        mock_get.return_value = Mock()
        mock_get.return_value.status_code = 200
        r = s.get('http://www.google.com')
        self.assertEqual(r.status_code, 200)

    @patch('requests.Session.options')
    def test_options(self, mock_options):
        s = requests.Session()
        mock_options.return_value = Mock()
        mock_options.return_value.status_code = 200
        r = s.options('http://www.google.com')
        self.assertEqual(r.status_code, 200)

    @patch('requests.Session.head')
    def test_head(self, mock_head):
        s = requests.Session()
        mock_head.return_value = Mock()
        mock_head.return_value.status_code = 200
        r = s.head('http://www.google.com')
        self.assertEqual(r.status_code, 200)

    @patch('requests.Session.post')
    def test_post(self, mock_post):
        s = requests.Session()
        mock_post.return_value = Mock()
        mock_post.return_value.status_code = 200
        r = s.post('http://www.google.com')
        self.assertEqual(r.status_code, 200)

    @patch('requests.Session.put')
    def test_put(self, mock_put):
        s = requests.Session()
        mock_put.return_value = Mock()
        mock_put.return_value.status_code = 200
        r = s.put('http://www.google.com')
        self.assertEqual(r.status_code, 200)

    @patch('requests.Session.patch')
    def test_patch(self, mock_patch):
        s = requests.Session()
        mock_patch.return_value = Mock()
        mock_patch.return_value.status_code = 200
        r = s.patch('http://www.google.com')
        self.assertEqual(r.status_code, 200)

    @patch('requests.Session.delete')
    def test_delete(self, mock_delete):
        s = requests.Session()
        mock_delete.return_value = Mock()
        mock_delete.return_value.status_code = 200
        r = s.delete('http://www.google.com')
        self.assertEqual(r.status_code, 200)

    @patch('requests.Session.close')
    def test_close(self, mock_close):
        s = requests.Session()
        mock_close.return_value = Mock()
        s.close()
        mock_close.assert_called_once()

if __name__ == '__main__':
    unittest.main()

import requests
import unittest
from unittest.mock import Mock, patch

class TestSession(unittest.TestCase):

    @patch('requests.Session.send')
    def test_send(self, mock_send):
        s = requests.Session()
        mock_send.return_value = Mock()
        mock_send.return_value.status_code = 200
        r = s.get('http://www.google.com')
        self.assertEqual(r.status_code, 200)

    @patch('requests.Session.get')
    def test_get(self, mock_get):
        s = requests.Session()
        mock_get.return_value = Mock()
        mock_get.return_value.status_code = 200
        r = s.get('http://www.google.com')
        self.assertEqual(r.status_code, 200)

    @patch('requests.Session.options')
    def test_options(self, mock_options):
        s = requests.Session()
        mock_options.return_value = Mock()
        mock_options.return_value.status_code = 200
        r = s.options('http://www.google.com')
        self.assertEqual(r.status_code, 200)

    @patch('requests.Session.head')
    def test_head(self, mock_head):
        s = requests.Session()
        mock_head.return_value = Mock()
        mock_head.return_value.status_code = 200
        r = s.head('http://www.google.com')
        self.assertEqual(r.status_code, 200)

    @patch('requests.Session.post')
    def test_post(self, mock_post):
        s = requests.Session()
        mock_post.return_value = Mock()
        mock_post.return_value.status_code = 200
        r = s.post('http://www.google.com')
        self.assertEqual(r.status_code, 200)

    @patch('requests.Session.put')
    def test_put(self, mock_put):
        s = requests.Session()
        mock_put.return_value = Mock()
        mock_put.return_value.status_code = 200
        r = s.put('http://www.google.com')
        self.assertEqual(r.status_code, 200)

    @patch('requests.Session.patch')
    def test_patch(self, mock_patch):
        s = requests.Session()
        mock_patch.return_value = Mock()
        mock_patch.return_value.status_code = 200
        r = s.patch('http://www.google.com')
        self.assertEqual(r.status_code, 200)

    @patch('requests.Session.delete')
    def test_delete(self, mock_delete):
        s = requests.Session()
        mock_delete.return_value = Mock()
        mock_delete.return_value.status_code = 200
        r = s.delete('http://www.google.com')
        self.assertEqual(r.status_code, 200)

    @patch('requests.Session.close')
    def test_close(self, mock_close):
        s = requests.Session()
        mock_close.return_value = Mock()
        s.close()
        mock_close.assert_called_once()

if __name__ == '__main__':
    unittest.main()