from sympy import Max, Min, Symbol, oo
from sympy.abc import x, y

p = Symbol('p', positive=True)
n = Symbol('n', negative=True)

print(Max(x, -2))
print(Max(x, -2).subs(x, 3))
print(Max(p, -2))
print(Max(x, y))
print(Max(x, y) == Max(y, x))
print(Max(x, Max(y, z)))
print(Max(n, 8, p, 7, -oo))
print(Max(1, x, oo))

print(Min(x, -2))
print(Min(x, -2).subs(x, 3))
print(Min(p, -3))
print(Min(x, y))
print(Min(n, 8, p, -7, p, oo))
print(Min(1, x, oo))