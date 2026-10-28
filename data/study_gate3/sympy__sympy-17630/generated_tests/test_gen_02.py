import sympy
from sympy import MatrixSymbol, MatMul, Add, Symbol, Subs, Tuple, S, Dummy, KroneckerDelta, Identity, Derivative, Mul, Add
from sympy.core import Basic, Expr, S, Symbol, Tuple, Dummy, KroneckerDelta, Derivative, MatMul, MatAdd, MatrixExpr

def test_matrix_symbol():
    # Test creation and shape
    A = MatrixSymbol('A', 3, 4)
    assert A.shape == (3, 4)
    assert A.name == 'A'
    
    # Test multiplication
    B = MatrixSymbol('B', 4, 3)
    result = A * B
    assert isinstance(result, MatMul)
    assert result.args[0] == A
    assert result.args[1] == B
    
    # Test non-commutativity
    assert A * B != B * A
    
    # Test substitution in shape
    n, m = sympy.symbols('n m')
    A = MatrixSymbol('A', n, m)
    new_A = A.subs(n, 3).subs(m, 4)
    assert new_A.shape == (3, 4)
    
    # Test substitution in name (if name is a symbol)
    name = Symbol('A')
    A = MatrixSymbol(name, 2, 3)
    assert A.name == 'A'
    # Substitute name with another symbol
    new_name = Symbol('B')
    new_A = A.subs(name, new_name)
    assert new_A.name == 'B'
    
    # Test is_commutative
    assert not A.is_commutative

if __name__ == "__main__":
    test_matrix_symbol()