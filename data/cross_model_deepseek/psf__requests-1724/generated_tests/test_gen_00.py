import requests
from requests.exceptions import InvalidSchema
import unittest
from unittest.mock import patch, Mock

class TestSession(unittest.TestCase):

    def setUp(self):
        self.session = requests.Session()
        self.session.mount('http://', requests.adapters.HTTPAdapter())
        self.session.mount('https://', requests.adapters.HTTPAdapter())

    def test_get_adapter(self):
        with self.assertRaises(InvalidSchema):
            self.session.get_adapter('ftp://example.com')

    @patch.object(requests.Session, 'request')
    def test_send(self, mock_request):
        mock_request.return_value = Mock()
        self.session.send(Mock())
        mock_request.assert_called_once()

    def test_close(self):
        with patch.object(requests.adapters.HTTPAdapter, 'close') as mock_close:
            self.session.close()
            mock_close.assert_called()

    def test_mount(self):
        adapter = Mock()
        self.session.mount('mock://', adapter)
        self.assertEqual(self.session.adapters['mock://'], adapter)

if __name__ == '__main__':
    unittest.main()