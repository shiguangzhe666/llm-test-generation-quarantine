import sympy
from sympy import symbols, Piecewise, IndexedBase, Idx, Matrix, MatrixSymbol, Eq, sin

x, tau = symbols('x tau')
len_y = 5
y = IndexedBase('y', shape=(len_y,))
t = IndexedBase('t', shape=(len_y,))
Dy = IndexedBase('Dy', shape=(len_y-1,))
i = Idx('i', len_y-1)
e = Eq(Dy[i], (y[i+1] - y[i])/(t[i+1] - t[i]))
mat = Matrix([x**2, Piecewise((x + 1, x > 0), (x, True)), sin(x)])
A = MatrixSymbol('A', 3, 1)

# Test ccode
print("C code:")
print(sympy.ccode(Piecewise((x + 1, x > 0), (x, True)), tau, standard='C89'))
print(sympy.ccode(e.rhs, assign_to=e.lhs, contract=False, standard='C89'))
print(sympy.ccode(mat, A, standard='C89'))

# Test fcode
print("\nFortran code:")
print(sympy.fcode(Piecewise((x + 1, x > 0), (x, True)), tau, standard=77))
print(sympy.fcode(e.rhs, assign_to=e.lhs, contract=False, standard=77))
print(sympy.fcode(mat, A, standard=77))

# Test cxxcode
print("\nC++ code:")
print(sympy.cxxcode(Piecewise((x + 1, x > 0), (x, True)), tau, standard='c++11'))
print(sympy.cxxcode(e.rhs, assign_to=e.lhs, contract=False, standard='c++11'))
print(sympy.cxxcode(mat, A, standard='c++11'))