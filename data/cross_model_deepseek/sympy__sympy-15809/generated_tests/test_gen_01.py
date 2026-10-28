from sympy import Max, Min, Symbol, oo, S
from sympy.abc import x, y

p = Symbol('p', positive=True)
n = Symbol('n', negative=True)

def test_max():
    assert Max(x, -2) == Max(x, -2)
    assert Max(x, -2).subs(x, 3) == 3
    assert Max(p, -2) == p
    assert Max(x, y) == Max(x, y)
    assert Max(x, y) == Max(y, x)
    assert Max(x, Max(y, z)) == Max(x, y, z)
    assert Max(n, 8, p, 7, -oo) == Max(8, p)
    assert Max(1, x, oo) == oo

def test_min():
    assert Min(x, -2) == Min(x, -2)
    assert Min(x, -2).subs(x, 3) == -2
    assert Min(p, -3) == -3
    assert Min(x, y) == Min(x, y)
    assert Min(n, 8, p, -7, p, oo) == Min(n, -7)

if __name__ == "__main__":
    test_max()
    test_min()