from sympy import symbols, Piecewise, IndexedBase, Idx, Matrix, MatrixSymbol, sin, Eq
from sympy.printing import ccode, fcode, cxxcode

x, tau = symbols("x, tau")
expr = Piecewise((x + 1, x > 0), (x, True))
print(ccode(expr, tau, standard='C89'))

len_y = 5
y = IndexedBase('y', shape=(len_y,))
t = IndexedBase('t', shape=(len_y,))
Dy = IndexedBase('Dy', shape=(len_y-1,))
i = Idx('i', len_y-1)
e = Eq(Dy[i], (y[i+1] - y[i])/(t[i+1] - t[i]))
print(ccode(e.rhs, assign_to=e.lhs, contract=False, standard='C89'))

mat = Matrix([x**2, Piecewise((x + 1, x > 0), (x, True)), sin(x)])
A = MatrixSymbol('A', 3, 1)
print(ccode(mat, A, standard='C89'))

print(fcode(expr, tau))

print(fcode(e.rhs, assign_to=e.lhs, contract=False))

print(fcode(mat, A))

print(cxxcode(expr, assign_to=tau, standard='c++11'))