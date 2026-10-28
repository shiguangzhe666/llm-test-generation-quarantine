from sympy import MatrixSymbol, Identity, symbols, Dummy, KroneckerDelta, Sum

A = MatrixSymbol('A', 3, 4)
B = MatrixSymbol('B', 4, 3)

print(2*A*B + Identity(3))

I + 2*A*B