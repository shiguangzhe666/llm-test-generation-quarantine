import pytest
import numpy as np
import pandas as pd
import warnings
from unittest import mock
from typing import Any, Hashable

from ..core import dtypes, duck_array_ops, indexing
from ..core.pycompat import is_duck_dask_array
from ..core.variable import Variable
from ..core.coder import (
    SerializationWarning,
    VariableCoder,
    _ElementwiseFunctionArray,
    lazy_elemwise_func,
    unpack_for_encoding,
    unpack_for_decoding,
    safe_setitem,
    pop_to,
    _apply_mask,
    CFMaskCoder,
    CFScaleOffsetCoder,
    UnsignedIntegerCoder,
)


def test_lazy_elemwise_func_dask_array():
    import dask.array as da
    arr = da.from_array(np.arange(5), chunks=2)
    func = lambda x: x * 2
    result = lazy_elemwise_func(arr, func, np.float64)
    assert isinstance(result, da.Array)
    assert np.array_equal(result.compute(), np.arange(5) * 2)


def test_lazy_elemwise_func_numpy_array():
    arr = np.arange(5)
    func = lambda x: x * 2
    result = lazy_elemwise_func(arr, func, np.float64)
    assert isinstance(result, _ElementwiseFunctionArray)
    assert np.array_equal(result.compute(), np.arange(5) * 2)


def test_unpack_for_encoding():
    var = Variable("dim", np.array([1, 2, 3]), attrs={"a": 1}, encoding={"b": 2})
    dims, data, attrs, encoding = unpack_for_encoding(var)
    assert dims == "dim"
    assert np.array_equal(data, np.array([1, 2, 3]))
    assert attrs == {"a": 1}
    assert encoding == {"b": 2}


def test_unpack_for_decoding():
    var = Variable("dim", np.array([1, 2, 3]), attrs={"a": 1}, encoding={"b": 2})
    dims, data, attrs, encoding = unpack_for_decoding(var)
    assert dims == "dim"
    assert np.array_equal(data, np.array([1, 2, 3]))
    assert attrs == {"a": 1}
    assert encoding == {"b": 2}


def test_safe_setitem_existing_key():
    d = {"a": 1}
    with pytest.raises(KeyError):
        safe_setitem(d, "a", 2)


def test_safe_setitem_new_key():
    d = {"a": 1}
    safe_setitem(d, "b", 2)
    assert d == {"a": 1, "b": 2}


def test_pop_to_existing_key():
    source = {"a": 1}
    dest = {}
    pop_to(source, "a", dest)
    assert dest == {"a": 1}
    assert source == {}


def test_pop_to_nonexistent_key():
    source = {"a": 1}
    dest = {}
    pop_to(source, "b", dest)
    assert dest == {}
    assert source == {"a": 1}


def test_pop_to_value_none():
    source = {"a": None}
    dest = {}
    pop_to(source, "a", dest)
    assert dest == {"a": None}
    assert source == {}


def test_apply_mask_single_value():
    data = np.array([1, 2, 3, 4])
    fill_value = 0
    result = _apply_mask(data, fill_value)
    assert np.array_equal(result, np.array([1, 2, 3, 4]))


def test_apply_mask_multiple_values():
    data = np.array([1, 2, 3, 4])
    fill_values = [0, 0]
    with pytest.warns(UserWarning):
        result = _apply_mask(data, fill_values)
    assert np.array_equal(result, np.array([1, 2, 3, 4]))


def test_cfmaskcoder_encode_no_fill():
    var = Variable("dim", np.array([1, 2, 3]), attrs={}, encoding={})
    coder = CFMaskCoder()
    result = coder.encode(var)
    assert np.array_equal(result.data, np.array([1, 2, 3]))


def test_cfmaskcoder_encode_single_fill():
    var = Variable("dim", np.array([1, 2, 3]), attrs={"_FillValue": 0}, encoding={})
    coder = CFMaskCoder()
    result = coder.encode(var)
    assert np.array_equal(result.data, np.array([1, 2, 3]))


def test_cfmaskcoder_encode_multiple_fill():
    var = Variable("dim", np.array([1, 2, 3]), attrs={"_FillValue": 0, "missing_value": 0}, encoding={})
    coder = CFMaskCoder()
    with pytest.warns(UserWarning):
        result = coder.encode(var)
    assert np.array_equal(result.data, np.array([1, 2, 3]))


def test_cfmaskcoder_encode_conflicting_fill():
    var = Variable("dim", np.array([1, 2, 3]), attrs={"_FillValue": 0, "missing_value": 1}, encoding={})
    coder = CFMaskCoder()
    with pytest.raises(ValueError):
        coder.encode(var)


def test_cfmaskcoder_decode_no_fill():
    var = Variable("dim", np.array([1, 2, 3]), attrs={}, encoding={})
    coder = CFMaskCoder()
    result = coder.decode(var)
    assert np.array_equal(result.data, np.array([1, 2, 3]))


def test_cfmaskcoder_decode_single_fill():
    var = Variable("dim", np.array([1, 2, 3]), attrs={"_FillValue": 0}, encoding={})
    coder = CFMaskCoder()
    result = coder.decode(var)
    assert np.array_equal(result.data, np.array([1, 2, 3]))


def test_cfmaskcoder_decode_multiple_fill():
    var = Variable("dim", np.array([1, 2, 3]), attrs={"_FillValue": 0, "missing_value": 0}, encoding={})
    coder = CFMaskCoder()
    with pytest.warns(UserWarning):
        result = coder.decode(var)
    assert np.array_equal(result.data, np.array([1, 2, 3]))


def test_cfmaskcoder_decode_conflicting_fill():
    var = Variable("dim", np.array([1, 2, 3]), attrs={"_FillValue": 0, "missing_value": 1}, encoding={})
    coder = CFMaskCoder()
    with pytest.raises(ValueError):
        coder.decode(var)


def test_cfscaleoffsetcoder_encode_no_scale_offset():
    var = Variable("dim", np.array([1, 2, 3]), attrs={}, encoding={})
    coder = CFScaleOffsetCoder()
    result = coder.encode(var)
    assert np.array_equal(result.data, np.array([1, 2, 3]))


def test_cfscaleoffsetcoder_encode_scale_only():
    var = Variable("dim", np.array([1, 2, 3]), attrs={"scale_factor": 2}, encoding={})
    coder = CFScaleOffsetCoder()
    result = coder.encode(var)
    assert np.array_equal(result.data, np.array([2, 4, 6]))


def test_cfscaleoffsetcoder_encode_offset_only():
    var = Variable("dim", np.array([1, 2, 3]), attrs={"add_offset": 1}, encoding={})
    coder = CFScaleOffsetCoder()
    result = coder.encode(var)
    assert np.array_equal(result.data, np.array([2, 3, 4]))


def test_cfscaleoffsetcoder_encode_both_scale_offset():
    var = Variable("dim", np.array([1, 2, 3]), attrs={"scale_factor": 2, "add_offset": 1}, encoding={})
    coder = CFScaleOffsetCoder()
    result = coder.encode(var)
    assert np.array_equal(result.data, np.array([3, 5, 7]))


def test_cfscaleoffsetcoder_decode_no_scale_offset():
    var = Variable("dim", np.array([1, 2, 3]), attrs={}, encoding={})
    coder = CFScaleOffsetCoder()
    result = coder.decode(var)
    assert np.array_equal(result.data, np.array([1, 2, 3]))


def test_cfscaleoffsetcoder_decode_scale_only():
    var = Variable("dim", np.array([2, 4, 6]), attrs={"scale_factor": 2}, encoding={})
    coder = CFScaleOffsetCoder()
    result = coder.decode(var)
    assert np.array_equal(result.data, np.array([1, 2, 3]))


def test_cfscaleoffsetcoder_decode_offset_only():
    var = Variable("dim", np.array([2, 3, 4]), attrs={"add_offset": 1}, encoding={})
    coder = CFScaleOffsetCoder()
    result = coder.decode(var)
    assert np.array_equal(result.data, np.array([1, 2, 3]))


def test_cfscaleoffsetcoder_decode_both_scale_offset():
    var = Variable("dim", np.array([3, 5, 7]), attrs={"scale_factor": 2, "add_offset": 1}, encoding={})
    coder = CFScaleOffsetCoder()
    result = coder.decode(var)
    assert np.array_equal(result.data, np.array([1, 2, 3]))


def test_unsignedintegercoder_encode_unsigned_true():
    var = Variable("dim", np.array([1, 2, 3]), attrs={"_Unsigned": "true"}, encoding={})
    coder = UnsignedIntegerCoder()
    result = coder.encode(var)
    assert np.array_equal(result.data, np.array([1, 2, 3]))
    assert result.attrs["_Unsigned"] == "true"


def test_unsignedintegercoder_encode_unsigned_false():
    var = Variable("dim", np.array([1, 2, 3]), attrs={"_Unsigned": "false"}, encoding={})
    coder = UnsignedIntegerCoder()
    result = coder.encode(var)
    assert np.array_equal(result.data, np.array([1, 2, 3]))
    assert "_Unsigned" not in result.attrs


def test_unsignedintegercoder_decode_unsigned_true():
    var = Variable("dim", np.array([1, 2, 3]), attrs={"_Unsigned": "true"}, encoding={})
    coder = UnsignedIntegerCoder()
    result = coder.decode(var)
    assert np.array_equal(result.data, np.array([1, 2, 3]))


def test_unsignedintegercoder_decode_unsigned_false():
    var = Variable("dim", np.array([1, 2, 3]), attrs={"_Unsigned": "false"}, encoding={})
    coder = UnsignedIntegerCoder()
    result = coder.decode(var)
    assert np.array_equal(result.data, np.array([1, 2, 3]))


def test_unsignedintegercoder_decode_non_integer():
    var = Variable("dim", np.array([1.0, 2.0, 3.0]), attrs={"_Unsigned": "true"}, encoding={})
    coder = UnsignedIntegerCoder()
    with pytest.warns(UserWarning):
        result = coder.decode(var)
    assert np.array_equal(result.data, np.array([1.0, 2.0, 3.0]))