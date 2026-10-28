import pytest
from xarray.coding.variables import (
    CFMaskCoder,
    CFScaleOffsetCoder,
    UnsignedIntegerCoder,
    unpack_for_decoding,
    unpack_for_encoding,
    safe_setitem,
    pop_to,
    _apply_mask,
    _scale_offset_decoding,
    _choose_float_dtype,
    lazy_elemwise_func,
)
from xarray.core.variable import Variable

def test_CFMaskCoder_encode():
    coder = CFMaskCoder()
    variable = Variable(dims=[], data=np.array([1, 2, 3]), attrs={"_FillValue": 0}, encoding={"_FillValue": 0})
    result = coder.encode(variable, name="test")
    assert (result.data == [1, 2, 3]).all()
    assert result.encoding["_FillValue"] == 0

def test_CFMaskCoder_encode_no_fill_value():
    coder = CFMaskCoder()
    variable = Variable(dims=[], data=np.array([1, 2, 3]))
    result = coder.encode(variable, name="test")
    assert (result.data == [1, 2, 3]).all()
    assert "_FillValue" not in result.encoding

def test_CFMaskCoder_encode_conflicting_fill_values():
    coder = CFMaskCoder()
    variable = Variable(dims=[], data=np.array([1, 2, 3]), attrs={"_FillValue": 0}, encoding={"missing_value": 0})
    with pytest.raises(ValueError):
        coder.encode(variable, name="test")

def test_CFMaskCoder_decode():
    coder = CFMaskCoder()
    variable = Variable(dims=[], data=np.array([1, 2, 3]), attrs={"_FillValue": 0}, encoding={"_FillValue": 0})
    result = coder.decode(variable, name="test")
    assert (result.data == [1, 2, 3]).all()
    assert "missing_value" not in result.encoding
    assert "._FillValue" not in result.attrs

def test_CFScaleOffsetCoder_encode():
    coder = CFScaleOffsetCoder()
    variable = Variable(dims=[], data=np.array([1, 2, 3]), attrs={"add_offset": 10}, encoding={"add_offset": 10})
    result = coder.encode(variable, name="test")
    assert (result.data == [11, 12, 13]).all()
    assert result.encoding["add_offset"] == 10

def test_CFScaleOffsetCoder_encode_no_offset():
    coder = CFScaleOffsetCoder()
    variable = Variable(dims=[], data=np.array([1, 2, 3]))
    result = coder.encode(variable, name="test")
    assert (result.data == [1, 2, 3]).all()
    assert "add_offset" not in result.encoding

def test_CFScaleOffsetCoder_decode():
    coder = CFScaleOffsetCoder()
    variable = Variable(dims=[], data=np.array([11, 12, 13]), attrs={"add_offset": 10}, encoding={"add_offset": 10})
    result = coder.decode(variable, name="test")
    assert (result.data == [1, 2, 3]).all()
    assert "add_offset" not in result.encoding

def test_UnsignedIntegerCoder_encode():
    coder = UnsignedIntegerCoder()
    variable = Variable(dims=[], data=np.array([1, -2, 3], dtype=np.int8), attrs={"_Unsigned": "true"}, encoding={"_Unsigned": "true"})
    result = coder.encode(variable, name="test")
    assert (result.data == [1, 254, 3]).all()
    assert result.encoding["_Unsigned"] == "true"

def test_UnsignedIntegerCoder_encode_no_unsigned():
    coder = UnsignedIntegerCoder()
    variable = Variable(dims=[], data=np.array([1, -2, 3], dtype=np.int8))
    result = coder.encode(variable, name="test")
    assert (result.data == [1, -2, 3]).all()
    assert "_Unsigned" not in result.encoding

def test_UnsignedIntegerCoder_decode():
    coder = UnsignedIntegerCoder()
    variable = Variable(dims=[], data=np.array([1, 254, 3], dtype=np.uint8), attrs={"_Unsigned": "true"}, encoding={"_Unsigned": "true"})
    result = coder.decode(variable, name="test")
    assert (result.data == [1, -2, 3]).all()
    assert "_Unsigned" not in result.attrs
    assert "_Unsigned" not in result.encoding

def test_UnsignedIntegerCoder_decode_no_unsigned():
    coder = UnsignedIntegerCoder()
    variable = Variable(dims=[], data=np.array([1, 254, 3], dtype=np.uint8))
    result = coder.decode(variable, name="test")
    assert (result.data == [1, 254, 3]).all()
    assert "_Unsigned" not in result.attrs
    assert "_Unsigned" not in result.encoding

def test_safe_setitem():
    dest = {"a": 1}
    safe_setitem(dest, "a", 2, name="test")
    assert dest == {"a": 2}
    with pytest.raises(ValueError):
        safe_setitem(dest, "a", 3, name="test")

def test_pop_to():
    source = {"a": 1, "b": 2}
    dest = {}
    pop_to(dest, source, "a", name="test")
    assert dest == {"a": 1}
    assert source == {"a": 1, "b": 2}

def test_apply_mask():
    data = np.array([0, 1, 2, 3, 4, 5, 6, 7, 8, 9])
    encoded_fill_values = [2, 3, 4, 5]
    decoded_fill_value = -9999
    transform = _apply_mask(data, encoded_fill_values, decoded_fill_value, np.int8)
    result = transform(data)
    assert (result == [0, 1, -9999, -9999, -9999, 5, 6, 7, 8, 9]).all()

def test_scale_offset_decoding():
    data = np.array([11, 12, 13])
    scale_factor = 2
    add_offset = 10
    dtype = np.int8
    transform = _scale_offset_decoding(data, scale_factor, add_offset, dtype)
    result = transform(data)
    assert (result == [1, 2, 3]).all()

def test_choose_float_dtype():
    dtype = np.int8
    add_offset = False
    result = _choose_float_dtype(dtype, add_offset)
    assert result == np.float32

def test_lazy_elemwise_func():
    data = np.array([1, 2, 3])
    transform = partial(np.asarray, dtype=np.uint8)
    result = lazy_elemwise_func(data, transform, np.uint8)
    assert (result == [1, 2, 3]).all()