from sympy import *

def test_min_max():
    x, y, z = symbols('x y z')
    p = Symbol('p', positive=True)
    n = Symbol('n', negative=True)

    assert Max(x, -2) == Max(x, -2)
    assert Max(x, -2).subs(x, 3) == 3
    assert Max(p, 8, p, 7, -oo) == Max(8, p)
    assert Max(1, x, oo) == oo

    assert Min(x, -2) == Min(x, -2)
    assert Min(x, -2).subs(x, 3) == -2
    assert Min(n, 8, p, -7, p, oo) == Min(n, -7)
    assert Min(1, x, oo) == -oo

    assert Max(x, y) == Max(y, x)
    assert Max(x, Max(y, z)) == Max(x, y, z)

    assert Min(x, y) == Min(y, x)
    assert Min(x, Min(y, z)) == Min(x, y, z)

    assert Max(x).is_infinite is True
    assert Min(x).is_infinite is False

    assert Max(x, 1, y, 2).is_infinite is True
    assert Min(x, 1, y, 2).is_infinite is False

    assert Max(x, y, evaluate=False) == Max(x, y)
    assert Min(x, y, evaluate=False) == Min(x, y)

    assert Max(x, y, evaluate=True) == Max(x, y)
    assert Min(x, y, evaluate=True) == Min(x, y)

    assert Max(x, y, z).fdiff(1) == Heaviside(y - x)
    assert Max(x, y, z).fdiff(2) == Heaviside(z - y)
    assert Max(x, y, z).fdiff(3) == Heaviside(z - x)

    assert Min(x, y, z).fdiff(1) == Heaviside(x - y)
    assert Min(x, y, z).fdiff(2) == Heaviside(x - z)
    assert Min(x, y, z).fdiff(3) == Heaviside(y - z)

    assert Max(x, y, z).rewrite(Piecewise) == Piecewise((x, x >= y and x >= z), (y, True))
    assert Min(x, y, z).rewrite(Piecewise) == Piecewise((x, x <= y and x <= z), (y, True))

test_min_max()

from sympy import *

def test_min_max():
    x, y, z = symbols('x y z')
    p = Symbol('p', positive=True)
    n = Symbol('n', negative=True)

    assert Max(x, -2) == Max(x, -2)
    assert Max(x, -2).subs(x, 3) == 3
    assert Max(p, 8, p, 7, -oo) == Max(8, p)
    assert Max(1, x, oo) == oo

    assert Min(x, -2) == Min(x, -2)
    assert Min(x, -2).subs(x, 3) == -2
    assert Min(n, 8, p, -7, p, oo) == Min(n, -7)
    assert Min(1, x, oo) == -oo

    assert Max(x, y) == Max(y, x)
    assert Max(x, Max(y, z)) == Max(x, y, z)

    assert Min(x, y) == Min(y, x)
    assert Min(x, Min(y, z)) == Min(x, y, z)

    assert Max(x).is_infinite is True
    assert Min(x).is_infinite is False

    assert Max(x, 1, y, 2).is_infinite is True
    assert Min(x, 1, y, 2).is_infinite is False

    assert Max(x, y, evaluate=False) == Max(x, y)
    assert Min(x, y, evaluate=False) == Min(x, y)

    assert Max(x, y, evaluate=True) == Max(x, y)
    assert Min(x, y, evaluate=True) == Min(x, y)

    assert Max(x, y, z).fdiff(1) == Heaviside(y - x)
    assert Max(x, y, z).fdiff(2) == Heaviside(z - y)
    assert Max(x, y, z).fdiff(3) == Heaviside(z - x)

    assert Min(x, y, z).fdiff(1) == Heaviside(x - y)
    assert Min(x, y, z).fdiff(2) == Heaviside(x - z)
    assert Min(x, y, z).fdiff(3) == Heaviside(y - z)

    assert Max(x, y, z).rewrite(Piecewise) == Piecewise((x, x >= y and x >= z), (y, True))
    assert Min(x, y, z).rewrite(Piecewise) == Piecewise((x, x <= y and x <= z), (y, True))

test_min_max()

from sympy import *

def test_min_max():
    x, y, z = symbols('x y z')
    p = Symbol('p', positive=True)
    n = Symbol('n', negative=True)

    assert Max(x, -2) == Max(x, -2)
    assert Max(x, -2).subs(x, 3) == 3
    assert Max(p, 8, p, 7, -oo) == Max(8, p)
    assert Max(1, x, oo) == oo

    assert Min(x, -2) == Min(x, -2)
    assert Min(x, -2).subs(x, 3) == -2
    assert Min(n, 8, p, -7, p, oo) == Min(n, -7)
    assert Min(1, x, oo) == -oo

    assert Max(x, y) == Max(y, x)
    assert Max(x, Max(y, z)) == Max(x, y, z)

    assert Min(x, y) == Min(y, x)
    assert Min(x, Min(y, z)) == Min(x, y, z)

    assert Max(x).is_infinite is True
    assert Min(x).is_infinite is False

    assert Max(x, 1, y, 2).is_infinite is True
    assert Min(x, 1, y, 2).is_infinite is False

    assert Max(x, y, evaluate=False) == Max(x, y)
    assert Min(x, y, evaluate=False) == Min(x, y)

    assert Max(x, y, evaluate=True) == Max(x, y)
    assert Min(x, y, evaluate=True) == Min(x, y)

    assert Max(x, y, z).fdiff(1) == Heaviside(y - x)
    assert Max(x, y, z).fdiff(2) == Heaviside(z - y)
    assert Max(x, y, z).fdiff(3) == Heaviside(z - x)

    assert Min(x, y, z).fdiff(1) == Heaviside(x - y)
    assert Min(x, y, z).fdiff(2) == Heaviside(x - z)
    assert Min(x, y, z).fdiff(3) == Heaviside(y - z)

    assert Max(x, y, z).rewrite(Piecewise) == Piecewise((x, x >= y and x >= z), (y, True))
    assert Min(x, y, z).rewrite(Piecewise) == Piecewise((x, x <= y and x <= z), (y, True))

test_min_max()

from sympy import *

def test_min_max():
    x, y, z = symbols('x y z')
    p = Symbol('p', positive=True)
    n = Symbol('n', negative=True)

    assert Max(x, -2) == Max(x, -2)
    assert Max(x, -2).subs(x, 3) == 3
    assert Max(p, 8, p, 7, -oo) == Max(8, p)
    assert Max(1, x, oo) == oo

    assert Min(x, -2) == Min(x, -2)
    assert Min(x, -2).subs(x, 3) == -2
    assert Min(n, 8, p, -7, p, oo) == Min(n, -7)
    assert Min(1, x, oo) == -oo

    assert Max(x, y) == Max(y, x)
    assert Max(x, Max(y, z)) == Max(x, y, z)

    assert Min(x, y) == Min(y, x)
    assert Min(x, Min(y, z)) == Min(x, y, z)

    assert Max(x).is_infinite is True
    assert Min(x).is_infinite is False

    assert Max(x, 1, y, 2).is_infinite is True
    assert Min(x, 1, y, 2).is_infinite is False

    assert Max(x, y, evaluate=False) == Max(x, y)
    assert Min(x, y, evaluate=False) == Min(x, y)

    assert Max(x, y, evaluate=True) == Max(x, y)
    assert Min(x, y, evaluate=True) == Min(x, y)

    assert Max(x, y, z).fdiff(1) == Heaviside(y - x)
    assert Max(x, y, z).fdiff(2) == Heaviside(z - y)
    assert Max(x, y, z).fdiff(3) == Heaviside(z - x)

    assert Min(x, y, z).fdiff(1) == Heaviside(x - y)
    assert Min(x, y, z).fdiff(2) == Heaviside(x - z)
    assert Min(x, y, z).fdiff(3) == Heaviside(y - z)

    assert Max(x, y, z).rewrite(Piecewise) == Piecewise((x, x >= y and x >= z), (y, True))
    assert Min(x, y, z).rewrite(Piecewise) == Piecewise((x, x <= y and x <= z), (y, True))

test_min_max()

from sympy import *

def test_min_max():
    x, y, z = symbols('x y z')
    p = Symbol('p', positive=True)
    n = Symbol('n', negative=True)

    assert Max(x, -2) == Max(x, -2)
    assert Max(x, -2).subs(x, 3) == 3
    assert Max(p, 8, p, 7, -oo) == Max(8, p)
    assert Max(1, x, oo) == oo

    assert Min(x, -2) == Min(x, -2)
    assert Min(x, -2).subs(x, 3) == -2
    assert Min(n, 8, p, -7, p, oo) == Min(n, -7)
    assert Min(1, x, oo) == -oo

    assert Max(x, y) == Max(y, x)
    assert Max(x, Max(y, z)) == Max(x, y, z)

    assert Min(x, y) == Min(y, x)
    assert Min(x, Min(y, z)) == Min(x, y, z)

    assert Max(x).is_infinite is True
    assert Min(x).is_infinite is False

    assert Max(x, 1, y, 2).is_infinite is True
    assert Min(x, 1, y, 2).is_infinite is False

    assert Max(x, y, evaluate=False) == Max(x, y)
    assert Min(x, y, evaluate=False) == Min(x, y)

    assert Max(x, y, evaluate=True) == Max(x, y)
    assert Min(x, y, evaluate=True) == Min(x, y)

    assert Max(x, y, z).fdiff(1) == Heaviside(y - x)
    assert Max(x, y, z).fdiff(2) == Heaviside(z - y)
    assert Max(x, y, z).fdiff(3) == Heaviside(z - x)

    assert Min(x, y, z).fdiff(1) == Heaviside(x - y)
    assert Min(x, y, z).fdiff(2) == Heaviside(x - z)
    assert Min(x, y, z).fdiff(3) == Heaviside(y - z)

    assert Max(x, y, z).rewrite(Piecewise) == Piecewise((x, x >= y and x >= z), (y, True))
    assert Min(x, y, z).rewrite(Piecewise) == Piecewise((x, x <= y and x <= z), (y, True))

test_min_max()