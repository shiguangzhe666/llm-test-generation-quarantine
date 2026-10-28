from sympy import symbols, Piecewise, IndexedBase, Idx, Eq, Matrix, MatrixSymbol, sin, print_ccode, print_fcode

x, tau = symbols('x tau')
expr = Piecewise((x + 1, x > 0), (x, True))
print_ccode(expr, tau, standard='C89')
print_fcode(expr, tau)

len_y = 5
y = IndexedBase('y', shape=(len_y,))
t = IndexedBase('t', shape=(len_y,))
Dy = IndexedBase('Dy', shape=(len_y-1,))
i = Idx('i', len_y-1)
e = Eq(Dy[i], (y[i+1] - y[i])/(t[i+1] - t[i]))
print_ccode(e.rhs, assign_to=e.lhs, contract=False, standard='C89')
print_fcode(e.rhs, assign_to=e.lhs, contract=False)

mat = Matrix([x**2, Piecewise((x + 1, x > 0), (x, True)), sin(x)])
A = MatrixSymbol('A', 3, 1)
print_ccode(mat, A, standard='C89')
print_fcode(mat, A)