from sympy import symbols, oo, Min, Max, S, Heaviside
from sympy.abc import x, y, p, n
from sympy.testing.pytest import raises

def test_max():
    assert Max(x, -2) == x
    assert Max(x, -2).subs(x, 3) == 3
    assert Max(p, -2) == p
    assert Max(x, y) == Max(x, y)
    assert Max(x, y) == Max(y, x)
    assert Max(x, Max(y, z)) == Max(x, y, z)
    assert Max(n, 8, p, 7, -oo) == Max(8, p)
    assert Max(1, x, oo) == oo

def test_min():
    assert Min(x, -2) == -2
    assert Min(p, -3) == -3
    assert Min(x, y) == Min(x, y)
    assert Min(n, 8, p, -7, p, oo) == Min(n, -7)

def test_max_fdiff():
    assert Max(x, -2).fdiff(1) == Heaviside(x + 2)
    assert Max(x, y).fdiff(1) == Heaviside(x - y)

def test_min_fdiff():
    assert Min(x, -2).fdiff(1) == Heaviside(-x - 2)
    assert Min(x, y).fdiff(1) == Heaviside(y - x)

def test_max_rewrite_as_Heaviside():
    assert Max(x, -2)._eval_rewrite_as_Heaviside(x, -2) == x*Heaviside(x + 2) - 2*Heaviside(-x - 2)

def test_min_rewrite_as_Heaviside():
    assert Min(x, -2)._eval_rewrite_as_Heaviside(x, -2) == -2*Heaviside(x + 2) + x*Heaviside(-x - 2)

def test_min_rewrite_as_Piecewise():
    assert Min(x, y)._eval_rewrite_as_Piecewise() == Piecewise((y, x > y), (x, True))

def test_max_is_positive():
    assert Max(x, y).is_positive == (x.is_positive | y.is_positive)

def test_min_is_positive():
    assert Min(x, y).is_positive == (x.is_positive & y.is_positive)

def test_max_is_negative():
    assert Max(x, y).is_negative == (x.is_negative & y.is_negative)

def test_min_is_negative():
    assert Min(x, y).is_negative == (x.is_negative | y.is_negative)

raises(ArgumentIndexError, lambda: Max(x, -2).fdiff(3))
raises(ArgumentIndexError, lambda: Min(x, -2).fdiff(3))