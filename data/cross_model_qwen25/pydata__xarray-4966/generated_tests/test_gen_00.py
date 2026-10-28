import numpy as np
import pandas as pd
from ..core.variable import Variable
from .variables import (
    CFMaskCoder,
    CFScaleOffsetCoder,
    UnsignedIntegerCoder
)

def test_cfmaskcoder_encode():
    coder = CFMaskCoder()
    variable = Variable(('x',), np.array([1, 2, 3]), {'_FillValue': -9999})
    encoded = coder.encode(variable, 'test')
    assert (encoded.data == [1, 2, 3]).all()
    assert encoded.encoding['_FillValue'] == -9999

def test_cfmaskcoder_encode_missing_value():
    coder = CFMaskCoder()
    variable = Variable(('x',), np.array([1, 2, -9999]), {'missing_value': -9999})
    encoded = coder.encode(variable, 'test')
    assert (encoded.data == [1, 2, np.nan]).all()
    assert encoded.encoding['missing_value'] == -9999

def test_cfmaskcoder_decode():
    coder = CFMaskCoder()
    variable = Variable(('x',), np.array([1, 2, np.nan]), {'_FillValue': -9999})
    decoded = coder.decode(variable, 'test')
    assert (decoded.data == [1, 2, -9999]).all()
    assert decoded.encoding['_FillValue'] == -9999

def test_cfmaskcoder_decode_missing_value():
    coder = CFMaskCoder()
    variable = Variable(('x',), np.array([1, 2, -9999]), {'missing_value': -9999})
    decoded = coder.decode(variable, 'test')
    assert (decoded.data == [1, 2, -9999]).all()
    assert decoded.encoding['missing_value'] == -9999

def test_cfscaleoffsetcoder_encode():
    coder = CFScaleOffsetCoder()
    variable = Variable(('x',), np.array([1, 2, 3]), {'scale_factor': 2.0, 'add_offset': 1.0})
    encoded = coder.encode(variable, 'test')
    assert (encoded.data == [2, 4, 6]).all()
    assert encoded.encoding['scale_factor'] == 2.0
    assert encoded.encoding['add_offset'] == 1.0

def test_cfscaleoffsetcoder_decode():
    coder = CFScaleOffsetCoder()
    variable = Variable(('x',), np.array([2, 4, 6]), {'scale_factor': 2.0, 'add_offset': 1.0})
    decoded = coder.decode(variable, 'test')
    assert (decoded.data == [1, 2, 3]).all()
    assert decoded.encoding['scale_factor'] == 2.0
    assert decoded.encoding['add_offset'] == 1.0

def test_unsignedintegercoder_encode():
    coder = UnsignedIntegerCoder()
    variable = Variable(('x',), np.array([1, 256, -1]), encoding={'_Unsigned': 'true'})
    encoded = coder.encode(variable, 'test')
    assert (encoded.data == [1, 256, 65535]).all()
    assert encoded.encoding['_Unsigned'] == 'true'

def test_unsignedintegercoder_decode():
    coder = UnsignedIntegerCoder()
    variable = Variable(('x',), np.array([1, 256, 65535]), encoding={'_Unsigned': 'true'})
    decoded = coder.decode(variable, 'test')
    assert (decoded.data == [1, 256, -1]).all()
    assert decoded.encoding['_Unsigned'] == 'true'

def test_unsignedintegercoder_decode_without_unsigned():
    coder = UnsignedIntegerCoder()
    variable = Variable(('x',), np.array([1, 256, 65535]))
    decoded = coder.decode(variable, 'test')
    assert (decoded.data == [1, 256, 65535]).all()
    assert '_Unsigned' not in decoded.encoding

def test_unsignedintegercoder_decode_with_false():
    coder = UnsignedIntegerCoder()
    variable = Variable(('x',), np.array([1, 256, 65535]), encoding={'_Unsigned': 'false'})
    decoded = coder.decode(variable, 'test')
    assert (decoded.data == [1, 256, -1]).all()
    assert decoded.encoding['_Unsigned'] == 'false'

def test_unsignedintegercoder_decode_with_invalid():
    coder = UnsignedIntegerCoder()
    variable = Variable(('x',), np.array([1, 256, 65535]), encoding={'_Unsigned': 'invalid'})
    decoded = coder.decode(variable, 'test')
    assert (decoded.data == [1, 256, 65535]).all()
    assert '_Unsigned' not in decoded.encoding

def test_invalid_fill_value():
    coder = CFMaskCoder()
    variable = Variable(('x',), np.array([1, 2, 3]), encoding={'_FillValue': -9999.0})
    with pytest.raises(ValueError):
        coder.encode(variable, 'test')

def test_invalid_scale_factor():
    coder = CFScaleOffsetCoder()
    variable = Variable(('x',), np.array([1, 2, 3]), encoding={'scale_factor': -1.0})
    with pytest.raises(ValueError):
        coder.encode(variable, 'test')

def test_invalid_add_offset():
    coder = CFScaleOffsetCoder()
    variable = Variable(('x',), np.array([1, 2, 3]), encoding={'add_offset': -1.0})
    with pytest.raises(ValueError):
        coder.encode(variable, 'test')