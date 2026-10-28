from sympy import Symbol
from sympy.physics.secondquant import F

a = Symbol('a', above_fermi=True)
i = Symbol('i', below_fermi=True)
p = Symbol('p')

F(a).is_below_fermi
False
F(i).is_below_fermi
True
F(p).is_below_fermi
True

The same applies to creation operators Fd

F(a).is_only_below_fermi
False
F(i).is_only_below_fermi
True
F(p).is_only_below_fermi
False

F(a).is_only_above_fermi
True
F(i).is_only_above_fermi
False
F(p).is_only_above_fermi
False

F(a).is_q_creator
0
F(i).is_q_creator
-1
F(p).is_q_creator
-1

F(a).is_q_annihilator
1
F(i).is_q_annihilator
0
F(p).is_q_annihilator
1

F(a).is_only_q_creator
False
F(i).is_only_q_creator
True
F(p).is_only_q_creator
False

F(a).is_only_q_annihilator
True
F(i).is_only_q_annihilator
False
F(p).is_only_q_annihilator
False

F(a)._latex(printer)
"a_{a}"
F(i)._latex(printer)
"a_{i}"
F(p)._latex(printer)
"a_{p}"