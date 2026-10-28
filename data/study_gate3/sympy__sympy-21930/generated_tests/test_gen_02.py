import pytest
from sympy import Symbol, Integer, sqrt, Eq, Matrix
from sympy.physics.secondquant import (
    Dagger, AnnihilateBoson, CreateBoson, FockStateBosonKet, FockStateBosonBra,
    FockStateFermionKet, FockStateFermionBra, B, Bd, AntiSymmetricTensor,
    SqOperator, BosonicOperator, Annihilator, Creator, FermionicOperator
)

def test_dagger_number():
    assert Dagger(5).doit() == -5

def test_dagger_annihilate_boson():
    b = B(1)
    assert Dagger(b).doit() == Bd(1)

def test_dagger_create_boson():
    b = Bd(1)
    assert Dagger(b).doit() == B(1)

def test_dagger_expression():
    x = Symbol('x')
    expr = B(x) + Bd(x)
    assert Dagger(expr).doit() == Bd(x) + B(x)

def test_antisymmetric_tensor_sorting():
    from sympy.physics.secondquant import AntiSymmetricTensor
    a = AntiSymmetricTensor(0, 1, 2)
    assert a.indices == (0, 1, 2)
    b = AntiSymmetricTensor(2, 1, 0)
    assert b.indices == (0, 1, 2)
    assert b.sign == -1

def test_antisymmetric_tensor_latex():
    from sympy.physics.secondquant import AntiSymmetricTensor
    a = AntiSymmetricTensor(0, 1, 2)
    assert a._latex() == "a_{0,1,2}"

def test_annihilate_boson_state():
    b = B(1)
    assert b.state == 1

def test_annihilate_boson_is_symbolic():
    b = B(Symbol('x'))
    assert b.is_symbolic() is True
    b = B(Integer(1))
    assert b.is_symbolic() is False

def test_annihilate_boson_apply():
    x = Symbol('x')
    state = FockStateBosonKet((x,))
    result = B(x).apply_operator(state)
    assert result == sqrt(x) * FockStateBosonKet((x - 1,))

def test_create_boson_apply():
    x = Symbol('x')
    state = FockStateBosonKet((x,))
    result = Bd(x).apply_operator(state)
    assert result == sqrt(x) * FockStateBosonKet((x + 1,))

def test_create_boson_is_symbolic():
    b = Bd(Symbol('x'))
    assert b.is_symbolic() is True
    b = Bd(Integer(1))
    assert b.is_symbolic() is False