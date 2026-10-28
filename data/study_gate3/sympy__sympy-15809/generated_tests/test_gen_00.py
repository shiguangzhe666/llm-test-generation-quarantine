import pytest
from sympy.functions.elementary.miscellaneous import Min, Max
from sympy import oo

def test_min_zero_arguments():
    """Test Min() with 0 arguments returns oo."""
    result = Min()
    assert result == oo

def test_min_positive_cases():
    """Test Min() with positive arguments returns the smallest argument."""
    assert Min(1, 2, 3) == 1
    assert Min(10, -5, 0) == -5
    assert Min(0.5, 0.2, 0.8) == 0.2

def test_min_mixed_signs():
    """Test Min() with mixed signs returns the smallest argument."""
    assert Min(-1, 1) == -1
    assert Min(1, -1, 2) == -1
    assert Min(-1, -2, -3) == -3

def test_min_empty_list():
    """Test Min() with an empty list raises an error."""
    with pytest.raises(TypeError):
        Min([])

def test_max_zero_arguments():
    """Test Max() with 0 arguments returns -oo."""
    result = Max()
    assert result == -oo

def test_max_positive_cases():
    """Test Max() with positive arguments returns the largest argument."""
    assert Max(1, 2, 3) == 3
    assert Max(10, -5, 0) == 10
    assert Max(0.5, 0.2, 0.8) == 0.8

def test_max_mixed_signs():
    """Test Max() with mixed signs returns the largest argument."""
    assert Max(-1, 1) == 1
    assert Max(1, -1, 2) == 2
    assert Max(-1, -2, -3) == -1

def test_max_empty_list():
    """Test Max() with an empty list raises an error."""
    with pytest.raises(TypeError):
        Max([])