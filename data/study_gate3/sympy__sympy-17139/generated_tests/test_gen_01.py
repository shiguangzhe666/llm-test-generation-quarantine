import pytest
from sympy.simplify.fu import simplify
from sympy import Symbol, I, cos, exp, pi

def test_simple_complex_exponent():
    x = Symbol('x')
    expr = x**(2*I*pi)
    expected = cos(2*pi*log(x))
    result = simplify(expr)
    assert result == expected, f"Expected {expected}, but got {result}"

def test_complex_exponent_with_cos():
    x = Symbol('x')
    expr = cos(x)**(2*I)
    expected = (exp(I*x) + exp(-I*x))**(2*I) / 2
    result = simplify(expr)
    assert result == expected, f"Expected {expected}, but got {result}"

def test_complex_exponent_with_negative_exponent():
    x = Symbol('x')
    expr = x**(-2*I*pi)
    expected = 1 / cos(2*pi*log(x))
    result = simplify(expr)
    assert result == expected, f"Expected {expected}, but got {result}"

def test_complex_exponent_with_zero_exponent():
    x = Symbol('x')
    expr = x**(0)
    expected = 1
    result = simplify(expr)
    assert result == expected, f"Expected {expected}, but got {result}"

def test_complex_exponent_with_one_exponent():
    x = Symbol('x')
    expr = x**(1)
    expected = x
    result = simplify(expr)
    assert result == expected, f"Expected {expected}, but got {result}"

def test_complex_exponent_with_negative_one_exponent():
    x = Symbol('x')
    expr = x**(-1)
    expected = 1 / x
    result = simplify(expr)
    assert result == expected, f"Expected {expected}, but got {result}"

def test_complex_exponent_with_symbolic_exponent():
    x = Symbol('x')
    expr = x**(I)
    expected = exp(I*log(x))
    result = simplify(expr)
    assert result == expected, f"Expected {expected}, but got {result}"

def test_complex_exponent_with_negative_symbolic_exponent():
    x = Symbol('x')
    expr = x**(-I)
    expected = exp(-I*log(x))
    result = simplify(expr)
    assert result == expected, f"Expected {expected}, but got {result}"

def test_complex_exponent_with_zero_symbolic_exponent():
    x = Symbol('x')
    expr = x**(0)
    expected = 1
    result = simplify(expr)
    assert result == expected, f"Expected {expected}, but got {result}"

def test_complex_exponent_with_inf_exponent():
    x = Symbol('x')
    expr = x**(I*oo)
    expected = 1 / x
    result = simplify(expr)
    assert result == expected, f"Expected {expected}, but got {result}"

def test_complex_exponent_with_neg_inf_exponent():
    x = Symbol('x')
    expr = x**(-I*oo)
    expected = x
    result = simplify(expr)
    assert result == expected, f"Expected {expected}, but got {result}"

def test_complex_exponent_with_nan_exponent():
    x = Symbol('x')
    expr = x**(I*nan)
    with pytest.raises(ValueError):
        simplify(expr)

def test_complex_exponent_with_non_numeric_exponent():
    x = Symbol('x')
    expr = x**(2*I*pi + 1)
    expected = x * cos(2*pi*log(x))
    result = simplify(expr)
    assert result == expected, f"Expected {expected}, but got {result}"