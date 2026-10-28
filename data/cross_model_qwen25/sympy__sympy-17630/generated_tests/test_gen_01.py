import sympy as sp
from sympy.matrices import MatrixSymbol, Identity, MatrixExpr, MatrixElement, Mul, Add, Sum, KroneckerDelta, Symbol, Dummy

# Test setup
A = MatrixSymbol('A', 3, 4)
B = MatrixSymbol('B', 4, 3)
C = MatrixSymbol('C', 3, 3)
x, y = sp.symbols('x y')

# Test MatrixSymbol creation
assert A.shape == (3, 4)
assert B.shape == (4, 3)
assert C.shape == (3, 3)

# Test MatrixElement
ae = MatrixElement(A, 1, 2)
assert ae.parent == A
assert ae.i == 1
assert ae.j == 2

# Test MatrixSymbol in expressions
expr = 2*A*B + Identity(3)
assert expr == 2*A*B + Identity(3)

# Test MatrixSymbol substitution
expr_sub = expr.subs(A, C)
assert expr_sub == 2*C*B + Identity(3)

# Test MatrixSymbol derivatives
deriv = A.diff(x)
assert isinstance(deriv, MatrixElement)
assert deriv == A.diff(A[i, j], x)

# Test MatrixElement derivatives
deriv_elem = ae.diff(x)
assert deriv_elem is S.Zero

# Test MatrixSymbol non-commutative property
assert A.is_commutative == False
assert A.is_symbol == True
assert A._diff_wrt == True

# Test MatrixSymbol shape checking
try:
    MatrixSymbol('D', -1, 2)
except ValueError as e:
    assert "Dimensions must be positive integers." in str(e)

try:
    MatrixSymbol('E', 2, 0)
except ValueError as e:
    assert "Dimensions must be positive integers." in str(e)

# Test MatrixSymbol call exception
try:
    A()
except TypeError as e:
    assert "object of type 'MatrixSymbol' has no len()" in str(e)

print("All tests passed.")