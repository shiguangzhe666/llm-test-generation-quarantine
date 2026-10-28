import sympy

def test_matrix_symbol():
    # Test creation of MatrixSymbol
    A = sympy.MatrixSymbol('A', 3, 4)
    assert A.shape == (3, 4)

    # Test substitution in MatrixSymbol
    B = A._eval_subs(A.shape, (2, 2))
    assert B.shape == (2, 2)

    # Test that MatrixSymbol is not callable
    try:
        A()
    except TypeError as e:
        assert str(e) == "<class 'sympy.matrices.expressions.MatrixSymbol'> object is not callable"

    # Test that MatrixSymbol can be used in Matrix Expressions
    I = sympy.Identity(3)
    expr = 2*A*A + I
    assert expr.shape == (3, 3)

    # Test MatrixSymbol can be differentiated
    x = sympy.Symbol('x')
    y = sympy.Symbol('y')
    f = A[0, 0]*x + A[1, 1]*y
    f_x = sympy.diff(f, x)
    f_y = sympy.diff(f, y)
    assert f_x == A[0, 0]
    assert f_y == A[1, 1]

    print("All tests pass")

test_matrix_symbol()

import sympy

def test_matrix_symbol():
    # Test creation of MatrixSymbol
    A = sympy.MatrixSymbol('A', 3, 4)
    assert A.shape == (3, 4)

    # Test substitution in MatrixSymbol
    B = A._eval_subs(A.shape, (2, 2))
    assert B.shape == (2, 2)

    # Test that MatrixSymbol is not callable
    try:
        A()
    except TypeError as e:
        assert str(e) == "<class 'sympy.matrices.expressions.MatrixSymbol'> object is not callable"

    # Test that MatrixSymbol can be used in Matrix Expressions
    I = sympyIdentity(3)
    expr = 2*A*A + I
    assert expr.shape == (3, 3)

    # Test MatrixSymbol can be differentiated
    x = sympy.Symbol('x')
    y = sympy.Symbol('y')
    f = A[0, 0]*x + A[1, 1]*y
    f_x = sympy.diff(f, x)
    f_y = sympy.diff(f, y)
    assert f_x == A[0, 0]
    assert f_y == A[1, 1]

    print("All tests pass")

test_matrix_symbol()