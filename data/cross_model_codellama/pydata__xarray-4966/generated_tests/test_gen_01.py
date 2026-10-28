import numpy as np
import pytest

from xarray.core.variable import Variable
from xarray.core.coding import variables


def test_cf_mask_coder():
    # Test encode and decode with CFMaskCoder
    coder = variables.CFMaskCoder()

    # Test encode with fill value
    variable = Variable(("x",), np.array([1, 2, 3, 4, 5]), {"_FillValue": 999})
    encoded = coder.encode(variable)
    assert encoded.data is not variable.data
    assert np.isnan(encoded.data[1])
    assert np.isnan(encoded.data[4])

    # Test decode with fill value
    decoded = coder.decode(encoded)
    assert decoded.data is not variable.data
    assert decoded.data.dtype == variable.data.dtype
    assert not np.isnan(decoded.data[1])
    assert not np.isnan(decoded.data[4])

    # Test encode without fill value
    variable = Variable(("x",), np.array([1, 2, 3, 4, 5]))
    encoded = coder.encode(variable)
    assert encoded.data is not variable.data
    assert not np.isnan(encoded.data[1])
    assert not np.isnan(encoded.data[4])

    # Test decode without fill value
    decoded = coder.decode(encoded)
    assert decoded.data is not variable.data
    assert decoded.data.dtype == variable.data.dtype
    assert not np.isnan(decoded.data[1])
    assert not np.isnan(decoded.data[4])


def test_cf_scale_offset_coder():
    # Test encode and decode with CFScaleOffsetCoder
    coder = variables.CFScaleOffsetCoder()

    # Test encode with scale_factor and add_offset
    variable = Variable(("x",), np.array([1, 2, 3, 4, 5]), {"scale_factor": 2, "add_offset": 1})
    encoded = coder.encode(variable)
    assert encoded.data is not variable.data
    assert np.all(encoded.data == np.array([2, 4, 6, 8, 10]))

    # Test decode with scale_factor and add_offset
    decoded = coder.decode(encoded)
    assert decoded.data is not variable.data
    assert decoded.data.dtype == variable.data.dtype
    assert np.all(decoded.data == np.array([1, 2, 3, 4, 5]))

    # Test encode without scale_factor and add_offset
    variable = Variable(("x",), np.array([1, 2, 3, 4, 5]))
    encoded = coder.encode(variable)
    assert encoded.data is not variable.data
    assert np.all(encoded.data == np.array([1, 2, 3, 4, 5]))

    # Test decode without scale_factor and add_offset
    decoded = coder.decode(encoded)
    assert decoded.data is not variable.data
    assert decoded.data.dtype == variable.data.dtype
    assert np.all(decoded.data == np.array([1, 2, 3, 4, 5]))


def test_unsigned_integer_coder():
    # Test encode and decode with UnsignedIntegerCoder
    coder = variables.UnsignedIntegerCoder()

    # Test encode with _Unsigned attribute
    variable = Variable(("x",), np.array([1, 2, 3, 4, 5]), {"_Unsigned": "true"})
    encoded = coder.encode(variable)
    assert encoded.data is not variable.data
    assert np.issubdtype(encoded.data.dtype, np.integer)
    assert not np.isnan(encoded.data[1])
    assert not np.isnan(encoded.data[4])

    # Test decode with _Unsigned attribute
    decoded = coder.decode(encoded)
    assert decoded.data is not variable.data
    assert decoded.data.dtype == variable.data.dtype
    assert not np.isnan(decoded.data[1])
    assert not np.isnan(decoded.data[4])

    # Test encode without _Unsigned attribute
    variable = Variable(("x",), np.array([1, 2, 3, 4, 5]))
    encoded = coder.encode(variable)
    assert encoded.data is not variable.data
    assert np.issubdtype(encoded.data.dtype, np.integer)
    assert not np.isnan(encoded.data[1])
    assert not np.isnan(encoded.data[4])

    # Test decode without _Unsigned attribute
    decoded = coder.decode(encoded)
    assert decoded.data is not variable.data
    assert decoded.data.dtype == variable.data.dtype
    assert not np.isnan(decoded.data[1])
    assert not np.isnan(decoded.data[4])


def test_all_coders():
    # Test all coders with a variety of inputs
    coders = [
        variables.CFMaskCoder(),
        variables.CFScaleOffsetCoder(),
        variables.UnsignedIntegerCoder(),
    ]
    for coder in coders:
        # Test encode and decode with fill value
        variable = Variable(("x",), np.array([1, 2, 3, 4, 5]), {"_FillValue": 999})
        encoded = coder.encode(variable)
        assert encoded.data is not variable.data
        decoded = coder.decode(encoded)
        assert decoded.data is not variable.data
        assert decoded.data.dtype == variable.data.dtype
        assert np.all(decoded.data == np.array([1, 2, 3, 4, 5]))

        # Test encode and decode without fill value
        variable = Variable(("x",), np.array([1, 2, 3, 4, 5]))
        encoded = coder.encode(variable)
        assert encoded.data is not variable.data
        decoded = coder.decode(encoded)
        assert decoded.data is not variable.data
        assert decoded.data.dtype == variable.data.dtype
        assert np.all(decoded.data == np.array([1, 2, 3, 4, 5]))