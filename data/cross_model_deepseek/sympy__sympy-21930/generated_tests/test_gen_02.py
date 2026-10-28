import pytest
from sympy import symbols, I, S, sqrt, simplify
from sympy.physics.secondquant import F, Bra, Dagger, CreateFermion, AnnihilateFermion

def test_fermionic_operators():
    a, i, p = symbols('a i p')

    # Test properties
    assert F(a).is_above_fermi == True
    assert F(i).is_below_fermi == True
    assert F(p).is_above_fermi == False

    assert F(a).is_only_below_fermi == False
    assert F(i).is_only_below_fermi == True
    assert F(p).is_only_below_fermi == False

    assert F(a).is_only_above_fermi == True
    assert F(i).is_only_above_fermi == False
    assert F(p).is_only_above_fermi == False

    assert CreateFermion(a).is_q_creator == -1
    assert CreateFermion(i).is_q_creator == 0
    assert CreateFermion(p).is_q_creator == 1

    assert AnnihilateFermion(a).is_q_annihilator == 1
    assert AnnihilateFermion(i).is_q_annihilator == 0
    assert AnnihilateFermion(p).is_q_annihilator == -1

    assert CreateFermion(a).is_only_q_creator == False
    assert CreateFermion(i).is_only_q_creator == True
    assert CreateFermion(p).is_only_q_creator == False

    assert AnnihilateFermion(a).is_only_q_annihilator == True
    assert AnnihilateFermion(i).is_only_q_annihilator == False
    assert AnnihilateFermion(p).is_only_q_annihilator == False

    # Test application of operators
    assert Dagger(F(a)).apply_operator(Bra(i)) == Bra(a)
    assert Dagger(F(i)).apply_operator(Bra(i)) == Bra(i)
    assert Dagger(F(p)).apply_operator(Bra(i)) == Bra(p)

    assert Dagger(CreateFermion(a)).apply_operator(Bra(i)) == Bra(a)
    assert Dagger(CreateFermion(i)).apply_operator(Bra(i)) == Bra(i)
    assert Dagger(CreateFermion(p)).apply_operator(Bra(i)) == Bra(p)

    assert Dagger(AnnihilateFermion(a)).apply_operator(Bra(i)) == Bra(a)
    assert Dagger(AnnihilateFermion(i)).apply_operator(Bra(i)) == Bra(i)
    assert Dagger(AnnihilateFermion(p)).apply_operator(Bra(i)) == Bra(p)

test_fermionic_operators()

import pytest
from sympy import symbols, I, S, sqrt, simplify
from sympy.physics.secondquant import F, Bra, Dagger, CreateFermion, AnnihilateFermion

def test_fermionic_operators():
    a, i, p = symbols('a i p')

    # Test properties
    assert F(a).is_above_fermi == True
    assert F(i).is_below_fermi == True
    assert F(p).is_above_fermi == False

    assert F(a).is_only_below_fermi == False
    assert F(i).is_only_below_fermi == True
    assert F(p).is_only_below_fermi == False

    assert F(a).is_only_above_fermi == True
    assert F(i).is_only_above_fermi == False
    assert F(p).is_only_above_fermi == False

    assert CreateFermion(a).is_q_creator == -1
    assert CreateFermion(i).is_q_creator == 0
    assert CreateFermion(p).is_q_creator == 1

    assert AnnihilateFermion(a).is_q_annihilator == 1
    assert AnnihilateFermion(i).is_q_annihilator == 0
    assert AnnihilateFermion(p).is_q_annihilator == -1

    assert CreateFermion(a).is_only_q_creator == False
    assert CreateFermion(i).is_only_q_creator == True
    assert CreateFermion(p).is_only_q_creator == False

    assert AnnihilateFermion(a).is_only_q_annihilator == True
    assert AnnihilateFermion(i).is_only_q_annihilator == False
    assert AnnihilateFermion(p).is_only_q_annihilator == False

    # Test application of operators
    assert Dagger(F(a)).apply_operator(Bra(i)) == Bra(a)
    assert Dagger(F(i)).apply_operator(Bra(i)) == Bra(i)
    assert Dagger(F(p)).apply_operator(Bra(i)) == Bra(p)

    assert Dagger(CreateFermion(a)).apply_operator(Bra(i)) == Bra(a)
    assert Dagger(CreateFermion(i)).apply_operator(Bra(i)) == Bra(i)
    assert Dagger(CreateFermion(p)).apply_operator(Bra(i)) == Bra(p)

    assert Dagger(AnnihilateFermion(a)).apply_operator(Bra(i)) == Bra(a)
    assert Dagger(AnnihilateFermion(i)).apply_operator(Bra(i)) == Bra(i)
    assert Dagger(AnnihilateFermion(p)).apply_operator(Bra(i)) == Bra(p)

test_fermionic_operators()

import pytest
from sympy import symbols, I, S, sqrt, simplify
from sympy.physics.secondquant import F, Bra, Dagger, CreateFermion, AnnihilateFermion

def test_fermionic_operators():
    a, i, p = symbols('a i p')

    # Test properties
    assert F(a).is_above_fermi == True
    assert F(i).is_below_fermi == True
    assert F(p).is_above_fermi == False

    assert F(a).is_only_below_fermi == False
    assert F(i).is_only_below_fermi == True
    assert F(p).is_only_below_fermi == False

    assert F(a).is_only_above_fermi == True
    assert F(i).is_only_above_fermi == False
    assert F(p).is_only_above_fermi == False

    assert CreateFermion(a).is_q_creator == -1
    assert CreateFermion(i).is_q_creator == 0
    assert CreateFermion(p).is_q_creator == 1

    assert AnnihilateFermion(a).is_q_annihilator == 1
    assert AnnihilateFermion(i).is_q_annihilator == 0
    assert AnnihilateFermion(p).is_q_annihilator == -1

    assert CreateFermion(a).is_only_q_creator == False
    assert CreateFermion(i).is_only_q_creator == True
    assert CreateFermion(p).is_only_q_creator == False

    assert AnnihilateFermion(a).is_only_q_annihilator == True
    assert AnnihilateFermion(i).is_only_q_annihilator == False
    assert AnnihilateFermion(p).is_only_q_annihilator == False

    # Test application of operators
    assert Dagger(F(a)).apply_operator(Bra(i)) == Bra(a)
    assert Dagger(F(i)).apply_operator(Bra(i)) == Bra(i)
    assert Dagger(F(p)).apply_operator(Bra(i)) == Bra(p)

    assert Dagger(CreateFermion(a)).apply_operator(Bra(i)) == Bra(a)
    assert Dagger(CreateFermion(i)).apply_operator(Bra(i)) == Bra(i)
    assert Dagger(CreateFermion(p)).apply_operator(Bra(i)) == Bra(p)

    assert Dagger(AnnihilateFermion(a)).apply_operator(Bra(i)) == Bra(a)
    assert Dagger(AnnihilateFermion(i)).apply_operator(Bra(i)) == Bra(i)
    assert Dagger(AnnihilateFermion(p)).apply_operator(Bra(i)) == Bra(p)

test_fermionic_operators()