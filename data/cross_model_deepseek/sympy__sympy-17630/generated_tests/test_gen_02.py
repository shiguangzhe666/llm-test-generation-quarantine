import unittest
from sympy import Matrix, MatrixSymbol, MatrixElement, Identity, symbols, S

class TestMatrixSymbol(unittest.TestCase):

    def setUp(self):
        self.A = MatrixSymbol('A', 3, 4)
        self.B = MatrixSymbol('B', 4, 3)
        self.X = symbols('X')

    def test_init(self):
        self.assertEqual(self.A.shape, (3, 4))
        self.assertEqual(self.B.shape, (4, 3))

    def test_subs(self):
        new = MatrixSymbol('A', 2, 2)
        self.assertEqual(self.A._subs(self.A, new), new)

    def test_entry(self):
        self.assertEqual(self.A._entry(0, 0), MatrixElement(self.A, 0, 0))

    def test_mul(self):
        self.assertEqual((self.A * self.B).shape, (3, 3))
        self.assertEqual((self.A * S.One).shape, (3, 4))

    def test_add(self):
        self.assertEqual((self.A + self.B).shape, (4, 3))
        self.assertEqual((self.A + S.Zero * self.A).shape, (3, 4))

    def test_pow(self):
        self.assertEqual((self.A ** 2).shape, (3, 3))

    def test_transpose(self):
        self.assertEqual(self.A.T.shape, (4, 3))

    def test_trace(self):
        self.assertEqual(self.A.trace(), 0)

    def test_det(self):
        self.assertEqual(self.A.det(), 0)

    def test_inv(self):
        self.assertEqual(self.A.inv(), self.A.inv())

    def test_eigenvals(self):
        self.assertEqual(self.A.eigenvals(), {})

    def test_norm(self):
        self.assertEqual(self.A.norm(), 0)

    def test_is_invertible(self):
        self.assertEqual(self.A.is_invertible(), False)

    def test_is_diagonal(self):
        self.assertEqual(self.A.is_diagonal(), True)

    def test_is_symmetric(self):
        self.assertEqual(self.A.is_symmetric(), False)

    def test_is_positive_definite(self):
        self.assertEqual(self.A.is_positive_definite(), False)

    def test_is_nonzero(self):
        self.assertEqual(self.A.is_nonzero(), False)

    def test_is_square(self):
        self.assertEqual(self.A.is_square(), True)

    def test_is_skew(self):
        self.assertEqual(self.A.is_skew(), False)

    def test_is_hermitian(self):
        self.assertEqual(self.A.is_hermitian(), False)

    def test_is_positive(self):
        self.assertEqual(self.A.is_positive(), False)

if __name__ == '__main__':
    unittest.main()

import unittest
from sympy import Matrix, MatrixSymbol, MatrixElement, Identity, symbols, S

class TestMatrixSymbol(unittest.TestCase):

    def setUp(self):
        self.A = MatrixSymbol('A', 3, 4)
        self.B = MatrixSymbol('B', 4, 3)
        self.X = symbols('X')

    def test_init(self):
        self.assertEqual(self.A.shape, (3, 4))
        self.assertEqual(self.B.shape, (4, 3))

    def test_subs(self):
        new = MatrixSymbol('A', 2, 2)
        self.assertEqual(self.A._subs(self.A, new), new)

    def test_entry(self):
        self.assertEqual(self.A._entry(0, 0), MatrixElement(self.A, 0, 0))

    def test_mul(self):
        self.assertEqual((self.A * self.B).shape, (3, 3))
        self.assertEqual((self.A * S.One).shape, (3, 4))

    def test_add(self):
        self.assertEqual((self.A + self.B).shape, (4, 3))
        self.assertEqual((self.A + S.Zero * self.A).shape, (3, 4))

    def test_pow(self):
        self.assertEqual((self.A ** 2).shape, (3, 3))

    def test_transpose(self):
        self.assertEqual(self.A.T.shape, (4, 3))

    def test_trace(self):
        self.assertEqual(self.A.trace(), 0)

    def test_det(self):
        self.assertEqual(self.A.det(), 0)

    def test_inv(self):
        self.assertEqual(self.A.inv(), self.A.inv())

    def test_eigenvals(self):
        self.assertEqual(self.A.eigenvals(), {})

    def test_norm(self):
        self.assertEqual(self.A.norm(), 0)

    def test_is_invertible(self):
        self.assertEqual(self.A.is_invertible(), False)

    def test_is_diagonal(self):
        self.assertEqual(self.A.is_diagonal(), True)

    def test_is_symmetric(self):
        self.assertEqual(self.A.is