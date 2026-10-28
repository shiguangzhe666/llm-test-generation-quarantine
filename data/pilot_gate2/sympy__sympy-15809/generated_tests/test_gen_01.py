import pytest
from sympy import symbols, oo
from sympy.functions.elementary.miscellaneous import Min, Max

def test_min_zero_args():
    assert Min() == oo

def test_max_zero_args():
    assert Max() == -oo

def test_min_one_arg():
    assert Min(5) == 5

def test_max_one_arg():
    assert Max(5) == 5

def test_min_multiple_args():
    assert Min(1, 2, 3) == 1

def test_max_multiple_args():
    assert Max(1, 2, 3) == 3

def test_min_mixed_numbers():
    assert Min(2, 3.5) == 2

def test_max_mixed_numbers():
    assert Max(2, 3.5) == 3.5

def test_min_symbolic():
    x = symbols('x')
    assert Min(x, 5) == Min(x, 5)

def test_max_symbolic():
    x = symbols('x')
    assert Max(x, 5) == Max(x, 5)

def test_min_neg_inf():
    assert Min(-oo, oo) == -oo

def test_max_pos_inf():
    assert Max(-oo, oo) == oo

def test_min_with_inf():
    assert Min(5, oo) == 5

def test_max_with_inf():
    assert Max(5, oo) == oo

def test_min_neg_inf_2():
    assert Min(-oo, 5) == -oo

def test_max_neg_inf_2():
    assert Max(-oo, 5) == 5

def test_min_boundary():
    assert Min(0, 1, -1) == -1

def test_max_boundary():
    assert Max(0, 1, -1) == 1

def test_min_with_symbols():
    x, y = symbols('x y')
    assert Min(x, y) == Min(x, y)

def test_max_with_symbols():
    x, y = symbols('x y')
    assert Max(x, y) == Max(x, y)