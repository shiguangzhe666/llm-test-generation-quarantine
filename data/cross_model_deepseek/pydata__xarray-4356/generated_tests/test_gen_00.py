import numpy as np
import pytest
from xarray.core import nanops

def test_replace_nan():
    arr = np.array([1, 2, np.nan, 4, np.nan, 5])
    expected_arr, expected_mask = np.array([1, 2, 0, 4, 0, 5]), np.array([False, False, True, False, True, False])
    result_arr, result_mask = nanops._replace_nan(arr, 0)
    assert np.array_equal(result_arr, expected_arr)
    assert np.array_equal(result_mask, expected_mask)

def test_maybe_null_out():
    arr = np.array([1, 2, 3, 4, 5])
    axis = 0
    mask = np.array([False, False, True, False, False])
    min_count = 2
    expected_result = np.array([1, 2, 3, np.nan, np.nan])
    result = nanops._maybe_null_out(arr, axis, mask, min_count)
    assert np.array_equal(result, expected_result)

def test_nan_argminmax_object():
    arr = np.array(['1', '2', np.nan, '4', '5'])
    axis = 0
    expected_result = 2
    result = nanops._nan_argminmax_object("argmin", np.inf, arr, axis)
    assert result == expected_result

def test_nan_minmax_object():
    arr = np.array(['1', '2', np.nan, '4', '5'])
    axis = 0
    expected_result = '1'
    result = nanops._nan_minmax_object("min", -np.inf, arr, axis)
    assert result == expected_result

def test_nanmin():
    arr = np.array([1, 2, np.nan, 4, np.nan, 5])
    expected_result = 1
    result = nanops.nanmin(arr)
    assert result == expected_result

def test_nanmax():
    arr = np.array([1, 2, np.nan, 4, np.nan, 5])
    expected_result = 5
    result = nanops.nanmax(arr)
    assert result == expected_result

def test_nanargmin():
    arr = np.array([1, 2, np.nan, 4, np.nan, 5])
    expected_result = 0
    result = nanops.nanargmin(arr)
    assert result == expected_result

def test_nanargmax():
    arr = np.array([1, 2, np.nan, 4, np.nan, 5])
    expected_result = 4
    result = nanops.nanargmax(arr)
    assert result == expected_result

def test_nansum():
    arr = np.array([1, 2, np.nan, 4, np.nan, 5])
    expected_result = 12
    result = nanops.nansum(arr)
    assert result == expected_result

def test_nanmean():
    arr = np.array([1, 2, np.nan, 4, np.nan, 5])
    expected_result = 2.5
    result = nanops.nanmean(arr)
    assert result == expected_result

def test_nanmedian():
    arr = np.array([1, 2, np.nan, 4, np.nan, 5])
    expected_result = 3
    result = nanops.nanmedian(arr)
    assert result == expected_result

def test_nanvar():
    arr = np.array([1, 2, np.nan, 4, np.nan, 5])
    expected_result = 2.5
    result = nanops.nanvar(arr)
    assert result == expected_result

def test_nanstd():
    arr = np.array([1, 2, np.nan, 4, np.nan, 5])
    expected_result = 1.5811388300841898
    result = nanops.nanstd(arr)
    assert np.isclose(result, expected_result)

def test_nanprod():
    arr = np.array([1, 2, np.nan, 4, np.nan, 5])
    expected_result = 40
    result = nanops.nanprod(arr)
    assert result == expected_result

def test_nancumsum():
    arr = np.array([1, 2, np.nan, 4, np.nan, 5])
    expected_result = np.array([1, 3, 3, 7, 7, 12])
    result = nanops.nancumsum(arr)
    assert np.array_equal(result, expected_result)

def test_nancumprod():
    arr = np.array([1, 2, np.nan, 4, np.nan, 5])
    expected_result = np.array([1, 2, 2, 8, 8, 40])
    result = nanops.nancumprod(arr)
    assert np.array_equal(result, expected_result)