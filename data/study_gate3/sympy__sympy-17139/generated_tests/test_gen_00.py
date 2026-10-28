from sympy.simplify.fu import simplify
from sympy import Symbol, I, cos, exp, pi

def test_simplify_powers_with_complex_exponents():
    # Positive case: Simplify a^b where b is a complex number
    x = Symbol('x')
    result = simplify(x**(2+3*I))
    expected = x**2 * x**(3*I)
    assert result == expected, f"Expected {expected}, got {result}"

    # Positive case: Simplify a^b where b is a complex number involving pi
    result = simplify(exp(pi*I/2)**x)
    expected = exp(pi*I*x/2)
    assert result == expected, f"Expected {expected}, got {result}"

    # Positive case: Simplify a^b where b is a complex number and a is negative
    result = simplify((-1)**(1/2))
    expected = I
    assert result == expected, f"Expected {expected}, got {result}"

    # Boundary condition: Simplify a^0 where a is any non-zero number
    result = simplify(2**0)
    expected = 1
    assert result == expected, f"Expected {expected}, got {result}"

    # Edge case: Simplify a^1 where a is any non-zero number
    result = simplify(2**1)
    expected = 2
    assert result == expected, f"Expected {expected}, got {result}"

    # Edge case: Simplify 0^b where b is a complex number
    result = simplify(0**(1+2*I))
    expected = 0
    assert result == expected, f"Expected {expected}, got {result}"

    # Edge case: Simplify a^b where a is 1 and b is any complex number
    result = simplify(1**(2+3*I))
    expected = 1
    assert result == expected, f"Expected {expected}, got {result}"

    # Error handling: Simplify a^b where a is 0 and b is a non-zero complex number
    result = simplify(0**(2+3*I))
    expected = 0
    assert result == expected, f"Expected {expected}, got {result}"

    # Error handling: Simplify a^b where a is 0 and b is 0 (indeterminate form)
    result = simplify(0**0)
    expected = 1  # Conventionally, 0^0 is often taken as 1 in symbolic computation
    assert result == expected, f"Expected {expected}, got {result}"

    # Error handling: Simplify a^b where a is a negative number and b is a non-integer complex number
    result = simplify((-2)**(1+1/2*I))
    expected = -2**(1/2) * I
    assert result == expected, f"Expected {expected}, got {result}"

    # Positive case: Simplify a^b where a is a trigonometric function and b is a complex number
    result = simplify(cos(pi/4)**(1+2*I))
    expected = cos(pi/4)**2 * cos(pi/4)**(2*I)
    assert result == expected, f"Expected {expected}, got {result}"

# Run the tests
if __name__ == "__main__":
    import pytest
    pytest.main([__file__])