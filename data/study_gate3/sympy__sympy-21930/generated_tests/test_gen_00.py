from sympy import Symbol
from sympy.physics.secondquant import F, Fd

# Define symbols with different assumptions
a = Symbol('a', above_fermi=True)
i = Symbol('i', below_fermi=True)
p = Symbol('p')

# Test is_restricted
assert F(a).is_restricted == 1
assert Fd(a).is_restricted == 1
assert F(i).is_restricted == -1
assert Fd(i).is_restricted == -1
assert F(p).is_restricted == 0
assert Fd(p).is_restricted == 0

# Test is_above_fermi
assert F(a).is_above_fermi is True
assert F(i).is_above_fermi is False
assert F(p).is_above_fermi is True

# Test is_below_fermi
assert F(a).is_below_fermi is False
assert F(i).is_below_fermi is True
assert F(p).is_below_fermi is True

# Test is_only_below_fermi
assert F(a).is_only_below_fermi is False
assert F(i).is_only_below_fermi is True
assert F(p).is_only_below_fermi is False

# Test is_only_above_fermi
assert F(a).is_only_above_fermi is True
assert F(i).is_only_above_fermi is False
assert F(p).is_only_above_fermi is False

# Test is_q_creator
assert F(a).is_q_creator == 0
assert F(i).is_q_creator == -1
assert F(p).is_q_creator == -1

# Test is_q_annihilator
assert F(a).is_q_annihilator == 1
assert F(i).is_q_annihilator == 0
assert F(p).is_q_annihilator == 1

# Test is_only_q_creator
assert F(a).is_only_q_creator is False
assert F(i).is_only_q_creator is True
assert F(p).is_only_q_creator is False

# Test is_only_q_annihilator
assert F(a).is_only_q_annihilator is True
assert F(i).is_only_q_annihilator is False
assert F(p).is_only_q_annihilator is False