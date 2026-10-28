from sympy import Symbol, Mul
from sympy.physics.secondquant import F

a = Symbol('a', above_fermi=True)
i = Symbol('i', below_fermi=True)
p = Symbol('p')

F(a).is_below_fermi
F(i).is_below_fermi
F(p).is_below_fermi

F(a).is_above_fermi
F(i).is_above_fermi
F(p).is_above_fermi

F(a).is_only_below_fermi
F(i).is_only_below_fermi
F(p).is_only_below_fermi

F(a).is_only_above_fermi
F(i).is_only_above_fermi
F(p).is_only_above_fermi

F(a).is_q_creator
F(i).is_q_creator
F(p).is_q_creator

F(a).is_q_annihilator
F(i).is_q_annihilator
F(p).is_q_annihilator

F(a).is_only_q_creator
F(i).is_only_q_creator
F(p).is_only_q_creator

F(a).is_only_q_annihilator
F(i).is_only_q_annihilator
F(p).is_only_q_annihilator

F(a).__repr__()
F(i).__repr__()
F(p).__repr__()

F(a)._latex(printer)
F(i)._latex(printer)
F(p)._latex(printer)

F(a).apply_operator(y)
F(i).apply_operator(y)
F(p).apply_operator(y)