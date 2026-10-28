import sympy
from sympy import MatrixSymbol, MatrixExpr, Add, Mul, Eq, S, symbols, Derivative, KroneckerDelta, Identity, Inverse, Dummy, Sum, Tuple, Basic, Symbol

def test_matrix_symbol():
    # Test MatrixSymbol creation and shape
    A = MatrixSymbol('A', 3, 4)
    assert A.shape == (3, 4)
    B = MatrixSymbol('B', 4, 3)
    
    # Test matrix multiplication and addition
    expr = 2 * A * B + Identity(3)
    assert isinstance(expr, Add)
    assert len(expr.args) == 2
    assert isinstance(expr.args[0], Mul)
    assert isinstance(expr.args[1], Identity)
    
    # Test substitution of shape
    A_sub = A.subs(A.shape, (4, 5))
    assert A_sub.shape == (4, 5)
    assert A_sub.name == 'A'  # Name remains unchanged
    
    # Test MatrixElement creation
    a11 = MatrixElement(A, 0, 0)
    assert a11.parent == A
    assert a, a11.i == 0
    assert a11.j == 0
    assert a11.doit() == A[0, 0]

def test_matrix_element_derivative():
    A = MatrixSymbol('A', 2, 2)
    a11 = MatrixElement(A, 0, 0)
    x = symbols('x')
    
    # Derivative of a11 with respect to x should be zero
    assert a11.diff(x) == S.Zero

def test_matrix_eq():
    A = MatrixSymbol('A', 2, 2)
    B = MatrixSymbol('B', 2, 2)
    expr = Eq(A, B)
    assert expr == Eq(A, B)
    
    # Check if A - B is ZeroMatrix
    diff = A - B
    assert diff.is_ZeroMatrix

def test_get_postprocessor():
    A = MatrixSymbol('A', 2, 2)
    scalar = 5
    
    # Test scalar multiplication with matrix
    expr = scalar * A
    assert isinstance(expr, Mul)
    assert expr.args[0] == scalar
    assert expr.args[1] == A

    # Test scalar addition with matrix
    expr = A + scalar
    assert isinstance(expr, Add)
    assert expr.args[0] == A
    assert expr.args[1] == scalar

if __name__ == "__main__":
    test_matrix_symbol()
    test_matrix_element_derivative()
    test_matrix_eq()
    test_get_postprocessor()
    print("All tests passed!")

