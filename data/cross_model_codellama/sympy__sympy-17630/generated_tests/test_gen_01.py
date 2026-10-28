from sympy import MatrixSymbol, Identity, symbols, Dummy

A = MatrixSymbol('A', 3, 4)  # A 3 by 4 Matrix
B = MatrixSymbol('B', 4, 3)  # A 4 by 3 Matrix
A.shape
(3, 4)
2*A*B + Identity(3)
I + 2*A*B

A = MatrixSymbol('A', 3, 4)  # A 3 by 4 Matrix
B = MatrixSymbol('B', 4, 3)  # A 4 by 3 Matrix
A.shape
(3, 4)
2*A*B + Identity(3)
I + 2*A*B