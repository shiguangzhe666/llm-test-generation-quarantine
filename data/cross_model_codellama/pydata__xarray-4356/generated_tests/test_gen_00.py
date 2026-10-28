import pytest
import numpy as np
from xarray.core.nanops import (
    _replace_nan,
    _maybe_null_out,
    _nan_argminmax_object,
    _nan_minmax_object,
    nanmin,
    nanmax,
    nanargmin,
    nanargmax,
    nansum,
    nanmean,
    nanmedian,
    nanvar,
    nanstd,
    nanprod,
    nancumsum,
    nancumprod,
)


def test_replace_nan():
    a = np.array([1, 2, 3, np.nan])
    expected_mask = np.array([False, False, False, True])
    expected_a = np.array([1, 2, 3, 0])
    result_a, result_mask = _replace_nan(a, 0)
    np.testing.assert_array_equal(result_a, expected_a)
    np.testing.assert_array_equal(result_mask, expected_mask)


def test_maybe_null_out():
    a = np.array([1, 2, 3, 4])
    mask = np.array([False, False, False, True])
    expected_result = np.array([1, 2, 3, np.nan])
    result = _maybe_null_out(a, None, mask)
    np.testing.assert_array_equal(result, expected_result)


def test_nan_argminmax_object():
    a = np.array([1, 2, 3, np.nan])
    expected_result = np.array(3)
    result = _nan_argminmax_object("argmin", dtypes.get_pos_infinity(a.dtype), a)
    np.testing.assert_array_equal(result, expected_result)


def test_nan_minmax_object():
    a = np.array([1, 2, 3, np.nan])
    expected_result = np.array(3)
    result = _nan_minmax_object("max", dtypes.get_neg_infinity(a.dtype), a)
    np.testing.assert_array_equal(result, expected_result)


def test_nansum():
    a = np.array([1, 2, 3, np.nan])
    expected_result = np.array(6)
    result = nansum(a)
    np.testing.assert_array_equal(result, expected_result)


def test_nanmean():
    a = np.array([1, 2, 3, np.nan])
    expected_result = np.array(2)
    result = nanmean(a)
    np.testing.assert_array_equal(result, expected_result)


def test_nanmedian():
    a = np.array([1, 2, 3, 4])
    expected_result = np.array(3)
    result = nanmedian(a)
    np.testing.assert_array_equal(result, expected_result)


def test_nanvar():
    a = np.array([1, 2, 3, np.nan])
    expected_result = np.array(2)
    result = nanvar(a)
    np.testing.assert_array_equal(result, expected_result)


def test_nanstd():
    a = np.array([1, 2, 3, np.nan])
    expected_result = np.array(1)
    result = nanstd(a)
    np.testing.assert_array_equal(result, expected_result)


def test_nanprod():
    a = np.array([1, 2, 3, np.nan])
    expected_result = np.array(6)
    result = nanprod(a)
    np.testing.assert_array_equal(result, expected_result)


def test_nancumsum():
    a = np.array([1, 2, 3, 4])
    expected_result = np.array([1, 3, 6, 10])
    result = nancumsum(a)
    np.testing.assert_array_equal(result, expected_result)


def test_nancumprod():
    a = np.array([1, 2, 3, 4])
    expected_result = np.array([1, 2, 6, 24])
    result = nancumprod(a)
    np.testing.assert_array_equal(result, expected_result)


if __name__ == "__main__":
    pytest.main(["-k", "test_nanops"])