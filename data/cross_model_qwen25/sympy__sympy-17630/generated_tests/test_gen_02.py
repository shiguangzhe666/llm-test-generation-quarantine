import sympy as sp

# Define symbols and matrix
A = sp.MatrixSymbol('A', 3, 4)
B = sp.MatrixSymbol('B', 4, 3)
C = sp.MatrixSymbol('C', 3, 3)

# Define expressions
expr1 = 2*A*B + sp.eye(3)
expr2 = A.T * C - C * A

# Print expressions
print(expr1)
print(expr2)