import sympy as sp
from sympy.abc import x, y
from sympy.core import S
from sympy.core.function import ArgumentIndexError
from sympy.core.numbers import oo

# Test cases for Min and Max

def test_Min_Max():
    # Test Min
    assert Min(x, -2).subs(x, 3) == -2
    assert Min(p, -3) == -3
    assert Min(x, y) == Min(x, y)
    assert Min(n, 8, p, -7, p, oo) == Min(n, -7)

    # Test Max
    assert Max(x, -2).subs(x, 3) == 3
    assert Max(p, -2) == p
    assert Max(x, y) == Max(x, y)
    assert Max(n, 8, p, 7, -oo) == Max(8, p)
    assert Max(1, x, oo) == oo

    # Test fdiff for Min
    assert Min(x, -2).fdiff(1) == Heaviside(-2 - x)
    assert Min(x, -2).fdiff(2) == Heaviside(x + 2)

    # Test fdiff for Max
    assert Max(x, -2).fdiff(1) == Heaviside(x + 2)
    assert Max(x, -2).fdiff(2) == Heaviside(-2 - x)

    # Test is_positive, is_nonnegative, is_negative for Min
    assert Min(x, -2).is_positive is None
    assert Min(x, -2).is_nonnegative is None
    assert Min(x, -2).is_negative is None

    # Test is_positive, is_nonnegative, is_negative for Max
    assert Max(x, -2).is_positive is None
    assert Max(x, -2).is_nonnegative is None
    assert Max(x, -2).is_negative is None

    # Test rewrite as Heaviside
    assert Min(x, -2)._eval_rewrite_as_Heaviside(x, -2) == -2
    assert Max(x, -2)._eval_rewrite_as_Heaviside(x, -2) == x

    # Test rewrite as Piecewise
    assert Min(x, y)._eval_rewrite_as_Piecewise() == Min(x, y)
    assert Max(x, y)._eval_rewrite_as_Piecewise() == Max(x, y)

    # Test fuzzy_or and fuzzy_and
    assert fuzzy_or([True, False]) is True
    assert fuzzy_or([False, False]) is False
    assert fuzzy_and([True, True]) is True
    assert fuzzy_and([True, False]) is False

test_Min_Max()