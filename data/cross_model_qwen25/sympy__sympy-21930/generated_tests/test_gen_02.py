from sympy import Symbol
from sympy.physics.secondquant import F, Fd, Dagger, BKet, FockStateFermionKet

# Test cases
a = Symbol('a', above_fermi=True)
i = Symbol('i', below_fermi=True)
p = Symbol('p')

# AnnihilateFermion tests
af = F(a)
print(f"af.is_above_fermi: {af.is_above_fermi}, Expected: True")
print(f"af.is_below_fermi: {af.is_below_fermi}, Expected: False")
print(f"af.is_only_below_fermi: {af.is_only_below_fermi}, Expected: False")
print(f"af.is_only_above_fermi: {af.is_only_above_fermi}, Expected: True")

af = F(i)
print(f"af.is_above_fermi: {af.is_above_fermi}, Expected: False")
print(f"af.is_below_fermi: {af.is_below_fermi}, Expected: True")
print(f"af.is_only_below_fermi: {af.is_only_below_fermi}, Expected: True")
print(f"af.is_only_above_fermi: {af.is_only_above_fermi}, Expected: False")

af = F(p)
print(f"af.is_above_fermi: {af.is_above_fermi}, Expected: False")
print(f"af.is_below_fermi: {af.is_below_fermi}, Expected: True")
print(f"af.is_only_below_fermi: {af.is_only_below_fermi}, Expected: True")
print(f"af.is_only_above_fermi: {af.is_only_above_fermi}, Expected: False")

# CreateFermion tests
cf = Fd(a)
print(f"cf.is_above_fermi: {cf.is_above_fermi}, Expected: True")
print(f"cf.is_below_fermi: {cf.is_below_fermi}, Expected: False")
print(f"cf.is_only_below_fermi: {cf.is_only_below_fermi}, Expected: False")
print(f"cf.is_only_above_fermi: {cf.is_only_above_fermi}, Expected: True")

cf = Fd(i)
print(f"cf.is_above_fermi: {cf.is_above_fermi}, Expected: False")
print(f"cf.is_below_fermi: {cf.is_below_fermi}, Expected: True")
print(f"cf.is_only_below_fermi: {cf.is_only_below_fermi}, Expected: True")
print(f"cf.is_only_above_fermi: {cf.is_only_above_fermi}, Expected: False")

cf = Fd(p)
print(f"cf.is_above_fermi: {cf.is_above_fermi}, Expected: False")
print(f"cf.is_below_fermi: {cf.is_below_fermi}, Expected: True")
print(f"cf.is_only_below_fermi: {cf.is_only_below_fermi}, Expected: True")
print(f"cf.is_only_above_fermi: {cf.is_only_above_fermi}, Expected: False")

# Apply operator tests
print(f"F(a).apply_operator(BKet((1,))): {F(a).apply_operator(BKet((1,)))}")
print(f"Fd(a).apply_operator(BKet((1,))): {Fd(a).apply_operator(BKet((1,)))}")