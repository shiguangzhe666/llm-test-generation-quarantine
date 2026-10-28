from sympy import Symbol
from sympy.physics.secondquant import F, Fd, AnnihilateFermion, CreateFermion

# Test cases
def test_fermionic_operators():
    a = Symbol('a', above_fermi=True)
    i = Symbol('i', below_fermi=True)
    p = Symbol('p')

    # Test AnnihilateFermion
    assert AnnihilateFermion(a).is_above_fermi
    assert not AnnihilateFermion(a).is_below_fermi
    assert AnnihilateFermion(a).is_only_above_fermi
    assert not AnnihilateFermion(a).is_only_below_fermi
    assert not AnnihilateFermion(a).is_q_creator
    assert AnnihilateFermion(a).is_q_annihilator == 1

    assert AnnihilateFermion(i).is_below_fermi
    assert not AnnihilateFermion(i).is_above_fermi
    assert not AnnihilateFermion(i).is_only_below_fermi
    assert AnnihilateFermion(i).is_only_above_fermi == 0
    assert AnnihilateFermion(i).is_q_creator == -1
    assert not AnnihilateFermion(i).is_q_annihilator

    assert AnnihilateFermion(p).is_below_fermi
    assert not AnnihilateFermion(p).is_above_fermi
    assert not AnnihilateFermion(p).is_only_below_fermi
    assert AnnihilateFermion(p).is_only_above_fermi == 0
    assert AnnihilateFermion(p).is_q_creator == -1
    assert not AnnihilateFermion(p).is_q_annihilator

    # Test CreateFermion
    assert CreateFermion(a).is_above_fermi
    assert not CreateFermion(a).is_below_fermi
    assert not CreateFermion(a).is_only_above_fermi
    assert CreateFermion(a).is_only_below_fermi == 0
    assert CreateFermion(a).is_q_creator == 0
    assert CreateFermion(a).is_q_annihilator == -1

    assert CreateFermion(i).is_below_fermi
    assert not CreateFermion(i).is_above_fermi
    assert CreateFermion(i).is_only_below_fermi
    assert not CreateFermion(i).is_only_above_fermi
    assert CreateFermion(i).is_q_creator == -1
    assert not CreateFermion(i).is_q_annihilator

    assert CreateFermion(p).is_below_fermi
    assert not CreateFermion(p).is_above_fermi
    assert CreateFermion(p).is_only_below_fermi
    assert not CreateFermion(p).is_only_above_fermi
    assert CreateFermion(p).is_q_creator == -1
    assert not CreateFermion(p).is_q_annihilator

test_fermionic_operators()