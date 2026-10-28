import pytest

from xarray.coding.variables import VariableCoder


def test_cf_mask_coder_encode():
    # Test encoding for a variable with no fill values
    var = Variable("x", np.arange(5))
    coder = VariableCoder()
    encoded_var = coder.encode(var)
    assert encoded_var.dims == var.dims
    assert encoded_var.data.dtype == var.data.dtype
    assert duck_array_ops.allclose_or_equiv(encoded_var.data, var.data)
    assert encoded_var.attrs == var.attrs
    assert encoded_var.encoding == var.encoding

    # Test encoding for a variable with a fill value
    var = Variable("x", np.arange(5), {"_FillValue": 0})
    coder = VariableCoder()
    encoded_var = coder.encode(var)
    assert encoded_var.dims == var.dims
    assert encoded_var.data.dtype == var.data.dtype
    assert duck_array_ops.allclose_or_equiv(encoded_var.data, var.data)
    assert encoded_var.attrs == var.attrs
    assert encoded_var.encoding == var.encoding

    # Test encoding for a variable with a missing_value
    var = Variable("x", np.arange(5), {"missing_value": 0})
    coder = VariableCoder()
    encoded_var = coder.encode(var)
    assert encoded_var.dims == var.dims
    assert encoded_var.data.dtype == var.data.dtype
    assert duck_array_ops.allclose_or_equiv(encoded_var.data, var.data)
    assert encoded_var.attrs == var.attrs
    assert encoded_var.encoding == var.encoding


def test_cf_mask_coder_decode():
    # Test decoding for a variable with no fill values
    var = Variable("x", np.arange(5))
    coder = VariableCoder()
    decoded_var = coder.decode(var)
    assert decoded_var.dims == var.dims
    assert decoded_var.data.dtype == var.data.dtype
    assert duck_array_ops.allclose_or_equiv(decoded_var.data, var.data)
    assert decoded_var.attrs == var.attrs
    assert decoded_var.encoding == var.encoding

    # Test decoding for a variable with a fill value
    var = Variable("x", np.arange(5), {"_FillValue": 0})
    coder = VariableCoder()
    decoded_var = coder.decode(var)
    assert decoded_var.dims == var.dims
    assert decoded_var.data.dtype == var.data.dtype
    assert duck_array_ops.allclose_or_equiv(decoded_var.data, var.data)
    assert decoded_var.attrs == var.attrs
    assert decoded_var.encoding == var.encoding

    # Test decoding for a variable with a missing_value
    var = Variable("x", np.arange(5), {"missing_value": 0})
    coder = VariableCoder()
    decoded_var = coder.decode(var)
    assert decoded_var.dims == var.dims
    assert decoded_var.data.dtype == var.data.dtype
    assert duck_array_ops.allclose_or_equiv(decoded_var.data, var.data)
    assert decoded_var.attrs == var.attrs
    assert decoded_var.encoding == var.encoding


def test_cf_scale_offset_coder_encode():
    # Test encoding for a variable with no scale or offset
    var = Variable("x", np.arange(5))
    coder = VariableCoder()
    encoded_var = coder.encode(var)
    assert encoded_var.dims == var.dims
    assert encoded_var.data.dtype == var.data.dtype
    assert duck_array_ops.allclose_or_equiv(encoded_var.data, var.data)
    assert encoded_var.attrs == var.attrs
    assert encoded_var.encoding == var.encoding

    # Test encoding for a variable with a scale factor
    var = Variable("x", np.arange(5), {"scale_factor": 2})
    coder = VariableCoder()
    encoded_var = coder.encode(var)
    assert encoded_var.dims == var.dims
    assert encoded_var.data.dtype == var.data.dtype
    assert duck_array_ops.allclose_or_equiv(encoded_var.data, var.data * 2)
    assert encoded_var.attrs == var.attrs
    assert encoded_var.encoding == var.encoding

    # Test encoding for a variable with an add offset
    var = Variable("x", np.arange(5), {"add_offset": 2})
    coder = VariableCoder()
    encoded_var = coder.encode(var)
    assert encoded_var.dims == var.dims
    assert encoded_var.data.dtype == var.data.dtype
    assert duck_array_ops.allclose_or_equiv(encoded_var.data, var.data + 2)
    assert encoded_var.attrs == var.attrs
    assert encoded_var.encoding == var.encoding

    # Test encoding for a variable with both a scale factor and an add offset
    var = Variable("x", np.arange(5), {"scale_factor": 2, "add_offset": 2})
    coder = VariableCoder()
    encoded_var = coder.encode(var)
    assert encoded_var.dims == var.dims
    assert encoded_var.data.dtype == var.data.dtype
    assert duck_array_ops.allclose_or_equiv(encoded_var.data, var.data * 2 + 2)
    assert encoded_var.attrs == var.attrs
    assert encoded_var.encoding == var.encoding


def test_cf_scale_offset_coder_decode():
    # Test decoding for a variable with no scale or offset
    var = Variable("x", np.arange(5))
    coder = VariableCoder()
    decoded_var = coder.decode(var)
    assert decoded_var.dims == var.dims
    assert decoded_var.data.dtype == var.data.dtype
    assert duck_array_ops.allclose_or_equiv(decoded_var.data, var.data)
    assert decoded_var.attrs == var.attrs
    assert decoded_var.encoding == var.encoding

    # Test decoding for a variable with a scale factor
    var = Variable("x", np.arange(5), {"scale_factor": 2})
    coder = VariableCoder()
    decoded_var = coder.decode(var)
    assert decoded_var.dims == var.dims
    assert decoded_var.data.dtype == var.data.dtype
    assert duck_array_ops.allclose_or_equiv(decoded_var.data, var.data / 2)
    assert decoded_var.attrs == var.attrs
    assert decoded_var.encoding == var.encoding

    # Test decoding for a variable with an add offset
    var = Variable("x", np.arange(5), {"add_offset": 2})
    coder = VariableCoder()
    decoded_var = coder.decode(var)
    assert decoded_var.dims == var.dims
    assert decoded_var.data.dtype == var.data.dtype
    assert duck_array_ops.allclose_or_equiv(decoded_var.data, var.data - 2)
    assert decoded_var.attrs == var.attrs
    assert decoded_var.encoding == var.encoding

    # Test decoding for a variable with both a scale factor and an add offset
    var = Variable("x", np.arange(5), {"scale_factor": 2, "add_offset": 2})
    coder = VariableCoder()
    decoded_var = coder.decode(var)
    assert decoded_var.dims == var.dims
    assert decoded_var.data.dtype == var.data.dtype
    assert duck_array_ops.allclose_or_equiv(decoded_var.data, var.data / 2 - 2)
    assert decoded_var.attrs == var.attrs
    assert decoded_var.encoding == var.encoding