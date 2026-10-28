import pytest
import numpy as np

# Assuming the functions are imported from the module under test
# For the purpose of this example, assume the following functions are available:
# _replace_nan, _maybe_null_out, _nan_argminmax_object, _nan_minmax_object
# nanmin, nanmax, nanargmin, nanargmax, nansum, nanmean, nanmedian, nanvar, nanstd, nanprod, nancumsum, nancumprod

def test_replace_nan_with_values():
    arr = np.array([1, np.nan, 3])
    val = 0
    result, mask = _replace_nan(arr, val)
    expected_result = np.array([1, 0, 3])
    expected_mask = np.array([False, True, False])
    assert np.array_equal(result, expected_result)
    assert np.array_equal(mask, expected_mask)

def test_replace_nan_no_values():
    arr = np.array([1, 2, 3])
    val = 0
    result, mask = _replace_nan(arr, val)
    expected_mask = np.array([False, False, False])
    assert np.array_equal(mask, expected_mask)

def test_replace_nan_int():
    arr = np.array([np.nan, 2, np.nan], dtype=np.float64)
    val = 0
    result, mask = _replace_nan(arr, val)
    expected_result = np.array([0, 2, 0], dtype=np.float64)
    expected_mask = np.array([True, False, True])
    assert np.array_equal(result, expected_result)
    assert np.array_equal(mask, expected_mask)

def test_maybe_null_out_min_count():
    result = np.array([1, 2, 3])
    axis = 0
    mask = np.array([False, False, False])
    min_count = 4
    modified_result = _maybe_null_out(result, axis, mask, min_count)
    assert np.isnan(modified_result)

def test_maybe_null_out_axis_none():
    result = np.array([1, 2, 3])
    axis = None
    mask = np.array([False, False, False])
    min_count = 2
    modified_result = _maybe_null_out(result, axis, mask, min_count)
    assert np.array_equal(modified_result, result)

def test_nanmin_all_nan():
    arr = np.array([np.nan, np.nan])
    with pytest.raises(ValueError):
        nanmin(arr)

def test_nanmin_with_values():
    arr = np.array([1, 2, np.nan])
    result = nanmin(arr)
    assert result == 1

def test_nanmax_all_nan():
    arr = np.array([np.nan, np.nan])
    with pytest.raises(ValueError):
        nanmax(arr)

def test_nanmax_with_values():
    arr = np.array([1, 2, np.nan])
    result = nanmax(arr)
    assert result == 2

def test_nansum_min_count():
    arr = np.array([1, 2, np.nan])
    result = n