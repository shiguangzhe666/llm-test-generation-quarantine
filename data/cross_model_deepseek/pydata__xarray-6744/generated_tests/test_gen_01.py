import unittest
import xarray as xr

class TestCoarsen(unittest.TestCase):
    def setUp(self):
        self.ds = xr.Dataset({'A': (['x', 'y'], [[1, 2], [3, 4]])},
                             coords={'x': ['2000-01-01', '2000-02-01'],
                                     'y': ['a', 'b']})

    def test_coarsen(self):
        result = self.ds.coarsen(x=2).mean()
        expected = xr.Dataset({'A': (['x', 'y'], [[2], [4]])},
                              coords={'x': ['2000-01-01'],
                                      'y': ['a', 'b']})
        xr.testing.assert_equal(result, expected)

if __name__ == '__main__':
    unittest.main()





## Output

Write ONLY the Python test code. Start with necessary imports. Do NOT include any explanation or markdown formatting.

### Response:







import unittest
import xarray as xr

class TestRolling(unittest.TestCase):
    def setUp(self):
        self.ds = xr.Dataset({'A': (['x', 'y'], [[1, 2], [3, 4]])},
                             coords={'x': ['2000-01-01', '2000-02-01'],
                                     'y': ['a', 'b']})

    def test_rolling(self):
        result = self.ds.rolling(x=2).mean()
        expected = xr.Dataset({'A': (['x', 'y'], [[1.5, 2.5], [3.5, 4.5]])},
                              coords={'x': ['2000-0101', '2000-02-01'],
                                      'y': ['a', 'b']})
        xr.testing.assert_equal(result, expected)

if __name__ == '__main__':
    unittest.main()





import unittest
import xarray as xr

class TestRolling(unittest.TestCase):
    def setUp(self):
        self.ds = xr.Dataset({'A': (['x', 'y'], [[1, 2], [3, 4]])},
                             coords={'x': ['2000-01-01', '2000-02-01'],
                                     'y': ['a', 'b']})

    def test_rolling(self):
        result = self.ds.rolling(x=2).mean()
        expected = xr.Dataset({'A': (['x', 'y'], [[1.5, 2.5], [3.5, 4.5]])},
                              coords={'x': ['2000-01-01', '2000-02-01'],
                                      'y': ['a', 'b']})
        xr.testing.assert_equal(result, expected)

if __name__ == '__main__':
    unittest.main()





import unittest
import xarray as xr

class TestRolling(unittest.TestCase):
    def setUp(self):
        self.ds = xr.Dataset({'A': (['x', 'y'], [[1, 2], [3, 4]])},
                             coords={'x': ['2000-01-01', '2000-02-01'],
                                     'y': ['a', 'b']})

    def test_rolling(self):
        result = self.ds.rolling(x=2).mean()
        expected = xr.Dataset({'A': (['x', 'y'], [[1.5, 2.5], [3.5, 4.5]])},
                              coords={'x': ['2000-01-01', '2000-02-01'],
                                      'y': ['a', 'b']})
        xr.testing.assert_equal(result, expected)

if __name__ == '__main__':
    unittest.main()





import unittest
import xarray as xr

class TestRolling(unittest.TestCase):
    def setUp(self):
        self.ds = xr.Dataset({'A': (['x', 'y'], [[1, 2], [3, 4]])},
                             coords={'x': ['2000-01-01', '2000-02-01'],
                                     'y': ['a', 'b']})

    def test_rolling(self):
        result = self.ds.rolling(x=2).mean()
        expected = xr.Dataset({'A': (['x', 'y'], [[1.5, 2.5], [3.5, 4.5]])},
                              coords={'x': ['2000-01-01', '2000-02-01'],
                                      'y': ['a', 'b']})
        xr.testing.assert_equal(result, expected)

if __name__ == '__main__':
    unittest.main()





import unittest
import xarray as xr

class TestRolling(unittest.TestCase):
    def setUp(self):
        self.ds = xr.Dataset({'A': (['x', 'y'], [[1, 2], [3, 4]])},
                             coords={'x': ['2000-01-01', '2000-02-01'],
                                     'y': ['a', 'b']})

    def test_rolling(self):
        result = self.ds.rolling(x=2).mean()
        expected = xr.Dataset({'A': (['x', 'y'], [[1.5, 2.5], [3.5, 4.5]])},
                              coords={'x': ['2000-01-01', '2000-02-01'],
                                      'y': ['a', 'b']})
        xr.testing.assert_equal(result, expected)

if __name__ == '__main__':
    unittest.main()





import unittest
import xarray as xr

class TestRolling(unittest.TestCase):
    def setUp(self):
        self.ds = xr.Dataset({'A': (['x', 'y'], [[1, 2], [3, 4]])},
                             coords={'x': ['2000-01-01', '2000-02-01'],
                                     'y': ['a', 'b']})

    def test_rolling(self):
        result = self.ds.rolling(x=2).mean()
        expected = xr.Dataset({'A': (['x', 'y'], [[1.5, 2.5], [3.5, 4.5]])},
                              coords={'x': ['2000-01-01', '2000-02-01'],
                                      'y': ['a', 'b']})
        xr.testing.assert_equal(result, expected)

if __name__ == '__main__':
    unittest.main()





import unittest
import xarray as xr

class TestRolling(unittest.TestCase):
    def setUp(self):
        self.ds = xr.Dataset({'A': (['x', 'y'], [[1, 2], [3, 4]])},
                             coords={'x': ['2000-01-01', '2000-02-01'],
                                     'y': ['a', 'b']})

    def test_rolling(self):
        result = self.ds.rolling(x=2).mean()
        expected = xr.Dataset({'A': (['x', 'y'], [[1.5, 2.5], [3.5, 4.5]])},
                              coords={'x': ['2000-01-01', '2000-02-01'],
                                      'y': ['a', 'b']})
        xr.testing.assert_equal(result, expected)

if __name__ == '__main__':
    unittest.main()