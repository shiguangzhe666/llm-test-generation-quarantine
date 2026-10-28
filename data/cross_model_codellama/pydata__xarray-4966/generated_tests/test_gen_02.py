import pytest
from xarray.coding.variables import (
    VariableCoder,
    CFMaskCoder,
    CFScaleOffsetCoder,
    UnsignedIntegerCoder,
)


def test_cf_mask_coder():
    # Tests for CFMaskCoder
    coder = CFMaskCoder()

    # Test encode
    variable = Variable(["time", "x"], [[1, 2], [3, 4]])
    variable.encoding = {"_FillValue": -9999}
    variable.attrs = {"missing_value": -9999}
    variable = coder.encode(variable)
    assert variable.data[0, 0] == 1
    assert variable.data[0, 1] == 2
    assert variable.data[1, 0] == 3
    assert variable.data[1, 1] == 4

    # Test decode
    variable = Variable(["time", "x"], [[1, 2], [3, 4]])
    variable.encoding = {"_FillValue": -9999}
    variable.attrs = {"missing_value": -9999}
    variable = coder.decode(variable)
    assert variable.data[0, 0] == 1
    assert variable.data[0, 1] == 2
    assert variable.data[1, 0] == 3
    assert variable.data[1, 1] == 4


def test_cf_scale_offset_coder():
    # Tests for CFScaleOffsetCoder
    coder = CFScaleOffsetCoder()

    # Test encode
    variable = Variable(["time", "x"], [[1, 2], [3, 4]])
    variable.encoding = {"scale_factor": 2, "add_offset": 3}
    variable = coder.encode(variable)
    assert variable.data[0, 0] == 2
    assert variable.data[0, 1] == 4
    assert variable.data[1, 0] == 6
    assert variable.data[1, 1] == 8

    # Test decode
    variable = Variable(["time", "x"], [[2, 4], [6, 8]])
    variable.encoding = {"scale_factor": 2, "add_offset": 3}
    variable = coder.decode(variable)
    assert variable.data[0, 0] == 1
    assert variable.data[0, 1] == 2
    assert variable.data[1, 0] == 3
    assert variable.data[1, 1] == 4


def test_unsigned_integer_coder():
    # Tests for UnsignedIntegerCoder
    coder = UnsignedIntegerCoder()

    # Test encode
    variable = Variable(["time", "x"], [[1, 2], [3, 4]])
    variable.encoding = {"_Unsigned": "true"}
    variable = coder.encode(variable)
    assert variable.data[0, 0] == 1
    assert variable.data[0, 1] == 2
    assert variable.data[1, 0] == 3
    assert variable.data[1, 1] == 4

    # Test decode
    variable = Variable(["time", "x"], [[1, 2], [3, 4]])
    variable.encoding = {"_Unsigned": "true"}
    variable = coder.decode(variable)
    assert variable.data[0, 0] == 1
    assert variable.data[0, 1] == 2
    assert variable.data[1, 0] == 3
    assert variable.data[1, 1] == 4


def test_variable_coder():
    # Tests for VariableCoder
    coder = VariableCoder()

    # Test encode
    variable = Variable(["time", "x"], [[1, 2], [3, 4]])
    variable.encoding = {"_FillValue": -9999}
    variable.attrs = {"missing_value": -9999}
    variable = coder.encode(variable)
    assert variable.data[0, 0] == 1
    assert variable.data[0, 1] == 2
    assert variable.data[1, 0] == 3
    assert variable.data[1, 1] == 4

    # Test decode
    variable = Variable(["time", "x"], [[1, 2], [3, 4]])
    variable.encoding = {"_FillValue": -9999}
    variable.attrs = {"missing_value": -9999}
    variable = coder.decode(variable)
    assert variable.data[0, 0] == 1
    assert variable.data[0, 1] == 2
    assert variable.data[1, 0] == 3
    assert variable.data[1, 1] == 4

    # Test encode with scale_factor and add_offset
    variable = Variable(["time", "x"], [[1, 2], [3, 4]])
    variable.encoding = {"scale_factor": 2, "add_offset": 3}
    variable = coder.encode(variable)
    assert variable.data[0, 0] == 2
    assert variable.data[0, 1] == 4
    assert variable.data[1, 0] == 6
    assert variable.data[1, 1] == 8

    # Test decode with scale_factor and add_offset
    variable = Variable(["time", "x"], [[2, 4], [6, 8]])
    variable.encoding = {"scale_factor": 2, "add_offset": 3}
    variable = coder.decode(variable)
    assert variable.data[0, 0] == 1
    assert variable.data[0, 1] == 2
    assert variable.data[1, 0] == 3
    assert variable.data[1, 1] == 4

    # Test encode with _Unsigned
    variable = Variable(["time", "x"], [[1, 2], [3, 4]])
    variable.encoding = {"_Unsigned": "true"}
    variable = coder.encode(variable)
    assert variable.data[0, 0] == 1
    assert variable.data[0, 1] == 2
    assert variable.data[1, 0] == 3
    assert variable.data[1, 1] == 4

    # Test decode with _Unsigned
    variable = Variable(["time", "x"], [[1, 2], [3, 4]])
    variable.encoding = {"_Unsigned": "true"}
    variable = coder.decode(variable)
    assert variable.data[0, 0] == 1
    assert variable.data[0, 1] == 2
    assert variable.data[1, 0] == 3
    assert variable.data[1, 1] == 4