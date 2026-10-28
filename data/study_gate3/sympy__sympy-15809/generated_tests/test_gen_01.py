import pytest
from sympy.functions.elementary.miscellaneous import Min, Max
from sympy import oo

def test_min_zero_args():
    result = Min()
    assert result == oo, f"Expected Min() with 0 args to return {oo}, got {result}"

def test_min_positive_case():
    result = Min(1, 2, 3)
    assert result == 1, f"Expected Min(1, 2, 3) to return 1, got {result}"

def test_min_negative_case():
    result = Min(-1, -2, -3)
    assert result == -3, f"Expected Min(-1, -2, -3) to return -3, got {result}"

def test_min_mixed_case():
    result = Min(-1, 0, 1)
    assert result == -1, f"Expected Min(-1, 0, 1) to return -1, got {result}"

def test_min_large_numbers():
    result = Min(1000000, -1000000, 2000000, -2000000)
    assert result == -1000000, f"Expected Min(1000000, -1000000, 2000000, -2000000) to return -1000000, got {result}"

def test_max_zero_args():
    result = Max()
    assert result == -oo, f"Expected Max() with 0 args to return {-oo}, got {result}"

def test_max_positive_case():
    result = Max(1, 2, 3)
    assert result == 3, f"Expected Max(1, 2, 3) to return 3, got {result}"

def test_max_negative_case():
    result = Max(-1, -2, -3)
    assert result == -1, f"Expected Max(-1, -2, -3) to return -1, got {result}"

def test_max_mixed_case():
    result = Max(-1, 0, 1)
    assert result == 1, f"Expected Max(-1, 0, 1) to return 1, got {result}"

def test_max_large_numbers():
    result = Max(1000000, -1000000, 2000000, -2000000)
    assert result == 2000000, f"Expected Max(1000000, -1000000, 2000000, -2000000) to return 2000000, got {result}"

def test_min_invalid_input():
    with pytest.raises(TypeError):
        Min("a", 1, 2)

def test_max_invalid_input():
    with pytest.raises(TypeError):
        Max("a", 1, 2)