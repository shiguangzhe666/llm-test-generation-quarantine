import sympy
from sympy import MatrixSymbol, Matrix, symbols, Derivative, KroneckerDelta, Identity, S, Add, Mul, Eq, ZeroMatrix, Dummy, pprint

def test_matrixsymbol():
    A = MatrixSymbol('A', 3, 4)
    B = MatrixSymbol('B', 4, 3)
    assert A.shape == (3, 4)
    assert B.shape == (4, 3)
    expr = 2*A*B + Identity(3)
    assert expr == 2*A*B + Identity(3)

def test_matrixelement():
    A = MatrixSymbol('A', 3, 4)
    elem = MatrixElement(A, 1, 2)
    assert elem.parent == A
    assert elem.i == 1
    assert elem.j == 2

def test_substitution():
    A = MatrixSymbol('A', 3, 3)
    B = MatrixSymbol('B', 3, 3)
    expr = A + B
    substituted = expr.subs(A, B)
    assert substituted == 2*B

def test_callable():
    A = MatrixSymbol('A', 3, 3)
    try:
        A()
    except TypeError:
        pass
    else:
        assert False, "Expected TypeError"

def test_derivative():
    A = MatrixSymbol('A', 2, 2)
    x = symbols('x')
    expr = A*x
    der = expr.diff(x)
    assert der == A

if __name__ == "__main__":
    test_matrixsymbol()
    test_matrixelement()
    test_substitution()
    test_callable()
    test_derivative()