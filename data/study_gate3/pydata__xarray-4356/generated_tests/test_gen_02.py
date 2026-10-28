import numpy as np
import pytest

def test_replace_nan_with_nans():
    a = np.array([1, np.nan, 3])
    val = 0
    result, mask = _replace_nan(a, val)
    assert np.array_equal(result, [1, 0, 3])
    assert np.array_equal(mask, [False, True, False])

def test_replace_nan_no_nans():
    a = np.array([1, 2, 3])
    val = 0
    result, mask = _replace_nan(a, val)
    assert np.array_equal(result, a)
    assert np.array_equal(mask, [False, False, False])

def test_replace_nan_object_type():
    a = np.array([1, np.nan, 'a'], dtype=object)
    val = 0
    result, mask = _replace_nan(a, val)
    assert np.array_equal(result, [1, 0, 'a'])
    assert np.array_equal(mask, [False, True, False])

def test_maybe_null_out_min_count():
    mask = np.array([True, True, False])
    result = np.array([1, 2, 3])
    axis = 0
    min_count = 2
    # mask.sum(axis) = 2, mask.shape[axis] = 3
    # 3 - 2 - 2 = -1 < 0 → null_mask is True
    # Fill result with fill_value at null_mask
    expected_result = np.array([np.nan, np.nan, 3])
    assert np.array_equal(_maybe_null_out(result, mask, axis, min_count), expected_result)

def test_maybe_null_out_no_min_count():
    mask = np.array([True, True, False])
    result = np.array([1, 2, 3])
    axis = 0
    min_count = 5  # min_count > valid count
    # No null_mask, so return result as-is
    assert np.array_equal(_maybe_null_out(result, mask, axis, min_count), result)

def test_nan_min_object_array():
    a = np.array([1, np.nan, 2], dtype=object)
    result = _nan_minmax_object(a, 'min')
    assert result == 1

def test_nan_max_object_array():
    a = np.array([1, np.nan, 2], dtype=object)
    result = _nan_minmax_object(a, 'max')
    assert result == 2

def test_nan_min_all_nan():
    a = np.array([np.nan, np.nan], dtype=object)
    with pytest.raises(ValueError):
        _nan_minmax_object(a, 'min')

def test_nanmin_numeric_array():
    a = np.array([1, np.nan, 3])
    result = nanmin(a)
    assert result == 1

def test_nanmin_object_array():
    a = np.array([1, np.nan, 'a'], dtype=object)
    result = nanmin(a)
    assert result == 1

def test_nanmin_all_nan():
    a = np.array([np.nan, np.nan], dtype=object)
    with pytest.raises(ValueError):
        nanmin(a)

def test_nanmax_numeric_array():
    a = np.array([1, np.nan, 3])
    result = nanmax(a)
    assert result == 3

def test_nanmax_object_array():
    a = np.array([1, np.nan, 'a'], dtype=object)
    result = nanmax(a)
    assert result == 'a'

def test_nanmax_all_nan():
    a = np.array([np.nan, np.nan], dtype=object)
    with pytest.raises(ValueError):
        nanmax(a)