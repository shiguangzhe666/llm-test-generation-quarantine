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

def test_min_negative_numbers():
    assert Min(-3, -5) == -5

def test_max_negative_numbers():
    assert Max(-3, -5) == -3

def test_min_multiple_args():
    assert Min(3, 1, 2) == 1

def test_max_multiple_args():
    assert Max(3, 1, 2) == 3

def test_min_mixed_numbers():
    assert Min(-2, 0, 5) == -2

def test_max_mixed_numbers():
    assert Max(-2, 0, 5) == 5