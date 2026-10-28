import sympy as sp
from sympy.abc import x, y
from sympy.core.function import Application

# Define the custom Max and Min classes
class Max(Application):
    pass

class Min(Application):
    pass

# Create instances of Max and Min
max_example = Max(x, -2)
min_example = Min(x, -2)

# Substitute values
max_example_sub = max_example.subs(x, 3)

# Check properties
max_is_positive = max_example.is_positive
min_is_negative = min_example.is_negative

# Print results
print(f"Max(x, -2).subs(x, 3): {max_example_sub}")
print(f"Max(x, -2).is_positive: {max_is_positive}")
print(f"Min(x, -2).is_negative: {min_is_negative}")