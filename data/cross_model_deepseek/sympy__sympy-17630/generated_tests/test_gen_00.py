import unittest
from sympy import MatrixSymbol, Matrix, Identity, symbols, I, S, simplify

class TestMatrixSymbol(unittest.TestCase):

    def setUp(self):
        self.A = MatrixSymbol('A', 3, 4)
        self.B = MatrixSymbol('B', 4, 3)
        self.X = MatrixSymbol('X', 3, 3)

    def test_creation(self):
        self.assertEqual(self.A.shape, (3, 4))
        self.assertEqual(self.B.shape, (4, 3))

    def test_subs(self):
        self.assertEqual(self.A._subs(self.A, self.X), self.X)

    def test_eval_subs(self):
        self.assertEqual(self.A.eval(subs={self.A: self.X}), self.X)

    def test_arithmetic(self):
        self.assertEqual(simplify(2*self.A*self.B + Identity(3)), I + 2*self.A*self.B)

if __name__name__ == '__main__':
    unittest.main()

import unittest
from sympy import MatrixSymbol, Matrix, Identity, symbols, I, S, simplify

class TestMatrixSymbol(unittest.TestCase):

    def setUp(self):
        self.A = MatrixSymbol('A', 3, 4)
        self.B = MatrixSymbol('B', 4, 3)
        self.X = MatrixSymbol('X', 3, 3)

    def test_creation(self):
        self.assertEqual(self.A.shape, (3, 4))
        self.assertEqual(self.B.shape, (4, 3))

    def test_subs(self):
        self.assertEqual(self.A._subs(self.A, self.X), self.X)

    def test_eval_subs(self):
        self.assertEqual(self.A.eval(subs={self.A: self.X}), self.X)

    def test_arithmetic(self):
        self.assertEqual(simplify(2*self.A*self.B + Identity(3)), I + 2*self.A*self.B)

if __name__ == '__main__':
    unittest.main()