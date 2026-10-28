import pytest
import numpy as np
import pandas as pd
from xarray.coding.variables import (
    CFMaskCoder,
    CFScaleOffsetCoder,
    UnsignedIntegerCoder,
    unpack_for_encoding,
    unpack_for_decoding,
    safe_setitem,
    pop_to,
    _apply_mask,
    _scale_offset_decoding,
    _choose_float_dtype,
    lazy_elemwise_func
)

def test_CFMaskCoder_encode():
    coder = CFMaskCoder()
    variable = Variable(('x', 'y'), np.array([[1, 2], [3, 4]]), {'_FillValue': 0})
    encoded = coder.encode(variable, name='test')
    assert np.array_equal(encoded.data, np.array([[1, 2], [3, 4]]))
    assert encoded.attrs == {'_FillValue': 0}
    assert encoded.encoding == {}

def test_CFMaskCoder_encode_with_missing_value():
    coder = CFMaskCoder()
    variable = Variable(('x', 'y'), np.array([[1, 2], [3, 4]]), {'missing_value': -9999})
    encoded = coder.encode(variable, name='test')
    assert np.array_equal(encoded.data, np.array([[1, 2], [3, 4]]))
    assert encoded.attrs == {'missing_value': -9999}
    assert encoded.encoding == {}

def test_CFMaskCoder_encode_with_conflicting_fill_values():
    coder = CFMaskCoder()
    variable = Variable(('x', 'y'), np.array([[1, 2], [3, 4]]), {'_FillValue': 0, 'missing_value': -9999})
    with pytest.raises(ValueError):
        coder.encode(variable, name='test')

def test_CFMaskCoder_decode():
    coder = CFMaskCoder()
    variable = Variable(('x', 'y'), np.array([[1, 2], [3, 4]]), {'_FillValue': 0})
    encoded = coder.encode(variable, name='test')
    decoded = coder.decode(encoded, name='test')
    assert np.array_equal(decoded.data, np.array([[1, 2], [3, 4]]))
    assert decoded.attrs == {'_FillValue': 0}
    assert decoded.encoding == {}

def test_CFScaleOffsetCoder_encode():
    coder = CFScaleOffsetCoder()
    variable = Variable(('x', 'y'), np.array([[1, 2], [3, 4]]), {'scale_factor': 2.0, 'add_offset': 1.0})
    encoded = coder.encode(variable, name='test')
    assert np.array_equal(encoded.data, np.array([[1, 2], [3, 4]]))
    assert encoded.attrs == {'scale_factor': 2.0, 'add_offset': 1.0}
    assert encoded.encoding == {}

def test_CFScaleOffsetCoder_decode():
    coder = CFScaleOffsetCoder()
    variable = Variable(('x', 'y'), np.array([[1, 2], [3, 4]]), {'scale_factor': 2.0, 'add_offset': 1.0})
    encoded = coder.encode(variable, name='test')
    decoded = coder.decode(encoded, name='test')
    assert np.array_equal(decoded.data, np.array([[3, 5], [7, 9]]))
    assert decoded.attrs == {'scale_factor': 2.0, 'add_offset': 1.0}
    assert decoded.encoding == {}

def test_UnsignedIntegerCoder_encode():
    coder = UnsignedIntegerCoder()
    variable = Variable(('x', 'y'), np.array([[1, 2], [3, 4]], dtype=np.int16), {'_Unsigned': 'true'})
    encoded = coder.encode(variable, name='test')
    assert np.array_equal(encoded.data, np.array([[1, 2], [3, 4]], dtype=np.uint16))
    assert encoded.attrs == {'_Unsigned': 'true'}
    assert encoded.encoding == {}

def test_UnsignedIntegerCoder_decode():
    coder = UnsignedIntegerCoder()
    variable = Variable(('x', 'y'), np.array([[1, 2], [3, 4]], dtype=np.uint16), {'_Unsigned': 'true'})
    encoded = coder.encode(variable, name='test')
    decoded = coder.decode(encoded, name='test')
    assert np.array_equal(decoded.data, np.array([[1, 2], [3, 4]], dtype=np.int16))
    assert decoded.attrs == {'_Unsigned': 'true'}
    assert decoded.encoding == {}

def test_UnsignedIntegerCoder_decode_with_non_integer():
    coder = UnsignedIntegerCoder()
    variable = Variable(('x', 'y'), np.array([[1.1, 2.2], [3.3, 4.4]], dtype=np.float32), {'_Unsigned': 'true'})
    encoded = coder.encode(variable, name='test')
    with pytest.warns(SerializationWarning):
        decoded = coder.decode(encoded, name='test')
    assert np.array_equal(decoded.data, np.array([[1.1, 2.2], [3.3, 4.4]], dtype=np.float32))
    assert decoded.attrs == {'_Unsigned': 'true'}
    assert decoded.encoding == {}

def test_safe_setitem():
    dest = {}
    safe_setitem(dest, 'a', 1, name='var')
    safe_setitem(dest, 'b', 2, name='var')
    assert dest == {'a': 1, 'b': 2}

def test_pop_to():
    source = {'_FillValue': 0, 'missing_value': -9999}
    dest = {}
    pop_to(dest, source, '_FillValue', name='var')
    pop_to(dest, source, 'missing_value', name='var')
    assert dest == {'_FillValue': 0, 'missing_value': -9999}

def test_apply_mask():
    data = np.array([1, 2, 3, 4, 5])
    encoded_fill_values = [2, 4]
    decoded_fill_value = np.nan
    transform = partial(_apply_mask, encoded_fill_values=encoded_fill_values, decoded_fill_value=decoded_fill_value, dtype=np.float64)
    masked_data = lazy_elemwise_func(data, transform, np.float64)
    assert np.array_equal(masked_data, [1, np.nan, 3, np.nan, 5])

def test_scale_offset_decoding():
    data = np.array([1, 2, 3, 4, 5])
    scale_factor = 2.0
    add_offset = 1.0
    transform = partial(_scale_offset_decoding, scale_factor=scale_factor, add_offset=add_offset, dtype=np.float64)
    scaled_data = lazy_elemwise_func(data, transform, np.float64)
    assert np.array_equal(scaled_data, [3, 5, 7, 9, 11])