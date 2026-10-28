from sympy import Symbol
from sympy.physics.secondquant import F, Fd, AnnihilateFermion, CreateFermion, FockStateFermionKet

# Test cases
def test_fermionic_operators():
    a = Symbol('a', above_fermi=True)
    i = Symbol('i', below_fermi=True)
    p = Symbol('p')

    # Annihilation operator tests
    assert F(a).is_above_fermi
    assert not F(i).is_above_fermi
    assert not F(p).is_above_fermi
    assert F(a).is_only_above_fermi
    assert F(i).is_only_below_fermi
    assert F(p).is_only_below_fermi
    assert F(a).is_q_annihilator == 1
    assert F(i).is_q_annihilator == 0
    assert F(p).is_q_annihilator == 0
    assert F(a).is_only_q_annihilator
    assert not F(i).is_only_q_annihilator
    assert not F(p).is_only_q_annihilator

    # Creation operator tests
    assert CreateFermion(a).is_above_fermi
    assert not CreateFermion(i).is_above_fermi
    assert not CreateFermion(p).is_above_fermi
    assert CreateFermion(a).is_only_above_fermi
    assert CreateFermion(i).is_only_below_fermi
    assert CreateFermion(p).is_only_below_fermi
    assert CreateFermion(a).is_q_creator == -1
    assert CreateFermion(i).is_q_creator == 0
    assert CreateFermion(p).is_q_creator == 0
    assert CreateFermion(a).is_only_q_creator
    assert not CreateFermion(i).is_only_q_creator
    assert not CreateFermion(p).is_only_q_creator

    # Application tests
    assert F(a).apply_operator(CreateFermion(a)) == 1
    assert CreateFermion(a).apply_operator(FockStateFermionKet((1,))) == FockStateFermionKet((2,))

test_fermionic_operators()