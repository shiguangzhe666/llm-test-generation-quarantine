import pytest
import numpy as np
from xarray.coding.variables import (
    VariableCoder,
    _ElementwiseFunctionArray,
    lazy_elemwise_func,
    safe_setitem,
    pop_to,
    _apply_mask,
    CFMaskCoder,
    CFScaleOffsetCoder,
    UnsignedIntegerCoder,
    Variable,
)

def test_VariableCoder():
    coder = VariableCoder()
    with pytest.raises(NotImplementedError):
        coder.encode(Variable())
    with pytest.raises(NotImplementedError):
        coder.decode(Variable())

def test__ElementwiseFunctionArray():
    array = np.array([1, 2, 3])
    func = lambda x: x**2
    ewfa = _ElementwiseFunctionArray(array, func)
    assert np.array_equal(ewfa, np.array([1, 4, 9]))

def test_lazy_elemwise_func():
    array = np.array([1, 2, 3])
    func = lambda x: x**2
    result = lazy_elemwise_func(array, func, np.float64)
    assert np.array_equal(result, np.array([1.0, 4.0, 9.0]))

def test_safe_setitem():
    d = {}
    safe_setitem(d, 'a', 1)
    assert d == {'a': 1}
    safe_setitem(d, 'a', 2)
    assert d == {'a': 2}

def test_pop_to():
    attrs = {'a': 1}
    encoding = {}
    result = pop_to(attrs, encoding, 'a')
    assert result == 1
    assert attrs == {}
    assert encoding == {}

def test__apply_mask():
    data = np.array([1, 2, 3])
    encoded_fill_values = {1, 2}
    result = _apply_mask(data, encoded_fill_values, np.nan, np.float64)
    assert np.array_equal(result, np.array([nan, nan, 3.0]))

def test_CFMaskCoder():
    coder = CFMaskCoder()
    variable = Variable()
    variable.encoding = {'a': 1}
    variable.attrs = {'b': 2}
    encoded = coder.encode(variable)
    assert encoded.attrs == {}
    assert encoded.encoding == {}
    decoded = coder.decode(encoded)
    assert decoded.attrs == {'b': 2}
    assert decoded.encoding == {'a': 1}

def test_CFScaleOffsetCoder():
    coder = CFScaleOffsetCoder()
    variable = Variable()
    variable.encoding = {'a': 1}
    variable.attrs = {'b': 2}
    encoded = coder.encode(variable)
    assert encoded.attrs == {}
    assert encoded.encoding == {}
    decoded = coder.decode(encoded)
    assert decoded.attrs == {'b': 2}
    assert decoded.encoding == {'a': 1}

def test_UnsignedIntegerCoder():
    coder = UnsignedIntegerCoder()
    variable = Variable()
    variable.encoding = {'a': 1}
    variable.attrs = {'b': 2}
    encoded = coder.encode(variable)
    assert encoded.attrs == {}
    assert encoded.encoding == {}
    decoded = coder.decode(encoded)
    assert decoded.attrs == {'b': 2}
    assert decoded.encoding == {'a': 1}