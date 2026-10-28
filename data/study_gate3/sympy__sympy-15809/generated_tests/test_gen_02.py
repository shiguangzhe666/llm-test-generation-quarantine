import pytest
from sympy.functions.elementary.miscellaneous import Min, Max
from sympy import oo, nan

# Test for Min function
def test_min_no_arguments():
    result = Min()
    assert result == oo, f"Min() with 0 arguments should return oo, got {result}"

def test_min_positive_case():
    result = Min(3, 1, 4, -1, 2)
    assert result == -1, f"Min(3, 1, 4, -1, 2) should return -1, got {result}"

def test_min_negative_case():
    result = Min(-3, -1, -4, -2)
    assert result == -4, f"Min(-3, -1, -4, -2) should return -4, got {result}"

def test_min_mixed_case():
    result = Min(0, -1, 1, -2, 2)
    assert result == -2, f"Min(0, -1, 1, -2, 2) should return -2, got {result}"

def test_min_nan():
    result = Min(nan, 1, 2)
    assert result == nan, f"Min(nan, 1, 2) should return nan, got {result}"

# Test for Max function
def test_max_no_arguments():
    result = Max()
    assert result == -oo, f"Max() with 0 arguments should return -oo, got {result}"

def test_max_positive_case():
    result = Max(3, 1, 4, -1, 2)
    assert result == 4, f"Max(3, 1, 4, -1, 2) should return 4, got {result}"

def test_max_negative_case():
    result = Max(-3, -1, -4, -2)
    assert result == -1, f"Max(-3, -1, -4, -2) should return -1, got {result}"

def test_max_mixed_case():
    result = Max(0, -1, 1, -2, 2)
    assert result == 2, f"Max(0, -1, 1, -2, 2) should return 2, got {result}"

def test_max_nan():
    result = Max(nan, 1, 2)
    assert result == 2, f"Max(nan, 1, 2) should return 2, got {result}"

def test_max_mixed_with_nan():
    result = Max(1, nan)
    assert result == 1, f"Max(1, nan) should return 1, got {result}"

def test_max_only_nan():
    result = Max(nan, nan)
    assert result == nan, f"Max(nan, nan) should return nan, got {result}"