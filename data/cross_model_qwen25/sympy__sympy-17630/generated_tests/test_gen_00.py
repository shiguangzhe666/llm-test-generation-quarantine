import sympy as sp

# Define symbols
A = sp.MatrixSymbol('A', 3, 4)
B = sp.MatrixSymbol('B', 4, 3)
C = sp.MatrixSymbol('C', 3, 3)

# Test matrix expressions
expr1 = 2*A*B + sp.eye(3)
expr2 = A.T * C - C * A.T

# Print the expressions
print(expr1)
print(expr2)

# Derivatives
expr3 = A[0, 1] + B[1, 2]
print(expr3.diff(A[0, 1]))

# Substitute in expressions
expr4 = 2*A*B + C
print(expr4.subs(C, sp.eye(3)))