import pytest
from sympy.simplify.fu import simplify
from sympy import Symbol, I, cos

def test_simplify_with_complex_exponent():
    # Define symbols
    x = Symbol('x')
    
    # Positive case: Simplify with a complex exponent
    result = simplify(x**(2*I))
    expected = cos(2 * x)
    assert result == expected, f"Expected {expected}, but got {result}"

    # Boundary condition: Simplify with a zero exponent
    result = simplify(x**(0*I))
    expected = 1
    assert result == expected, f"Expected {expected}, but got {result}"

    # Edge case: Simplify with a negative complex exponent
    result = simplify(x**(-2*I))
    expected = 1 / cos(2 * x)
    assert result == expected, f"Expected {expected}, but got {result}"

    # Edge case: Simplify with a complex exponent of 1
    result = simplify(x**(1*I))
    expected = I * x
    assert result == expected, f"Expected {expected}, but got {result}"

    # Edge case: Simplify with a complex exponent of -1
    result = simplify(x**(-1*I))
    expected = -I * x
    assert result == expected, f"Expected {expected}, but got {result}"

    # Edge case: Simplify with a complex exponent of a fraction
    result = simplify(x**(0.5*I))
    expected = x**0.5 * I
    assert result == expected, f"Expected {expected}, but got {result}"

    # Error handling: Simplify with a non-numeric exponent
    with pytest.raises(TypeError):
        simplify(x**('I'))

    # Error handling: Simplify with a zero base and complex exponent
    with pytest.raises(ZeroDivisionError):
        simplify(0**(2*I))

    # Error handling: Simplify with a negative base and complex exponent
    with pytest.raises(ZeroDivisionError):
        simplify((-1)**(2*I))