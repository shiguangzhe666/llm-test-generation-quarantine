import pytest
from sympy.functions.elementary.miscellaneous import Min, Max
from sympy import oo

def test_min_zero_args():
    assert Min() == oo

def test_max_zero_args():
    assert Max() == -oo

def test_min_one_arg():
    assert Min(5) == 5

def test_max_one_arg():
    assert Max(5) == 5

def test_min_two_args():
    assert Min(1, 2) == 1

def test_max_two_args():
    assert Max(1, 2) == 2

def test_min_negative():
    assert Min(-5, -3) == -5

def test_max_negative():
    assert Max(-5, -3) == -3

def test_min_mixed():
    assert Min(2, -1) == -1

def test_max_mixed():
    assert Max(2, -1) == 2

def test_min_multiple_args():
    assert Min(3, 1, 4) == 1

def test_max_multiple_args():
    assert Max(3, 1, 4) == 4

def test_min_with_zero():
    assert Min(0) == 0

def test_max_with_zero():
    assert Max(0) == 0

def test_min_with_positive_and_negative():
    assert Min(3, -2, 0) == -2

def test_max_with_positive_and_negative():
    assert Max(3, -2, 0) == 3

def test_min_with_duplicate_values():
    assert Min(2, 2, 3) == 2

def test_max_with_duplicate_values():
    assert Max(2, 2, 3) == 3