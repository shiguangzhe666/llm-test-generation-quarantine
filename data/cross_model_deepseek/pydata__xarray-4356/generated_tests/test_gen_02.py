import numpy as np
import pytest
import xarray.core.nanops as nanops

def test_replace_nan():
    arr = np.array([1, 2, np.nan, 3, np.nan, 4])
    expected_val = 99
    result, mask = nanops._replace_nan(arr, expected_val)
    assert np.isnan(result[2]).all()
    assert np.isnan(result[4]).all()
    assert (result[:2] == arr[:2]).all()
    assert (result[3:] == arr[4:]).all()
    assert (mask == np.array([0, 0, 1, 0, 1, 0])).all()

def test_maybe_null_out():
    arr = np.array([1, 2, 3, 4])
    axis = 0
    mask = np.array([0, 0, 1, 0])
    result = nanops._maybe_null_out(arr, axis, mask, min_count=1)
    assert (result == np.array([1, 2, np.nan, 4])).all()

def test_nan_argminmax_object():
    arr = np.array([1, 2, np.nan, 3, np.nan, 4])
    expected_val = 99
    result = nanops._nan_argminmax_object("argmin", expected_val, arr, axis=0)
    assert result == 0

def test_nan_minmax_object():
    arr = np.array([1, 2, np.nan, 3, np.nan, 4])
    expected_val = 99
    result = nanops._nan_minmax_object("min", expected_val, arr, axis=0)
    assert result == 1

def test_nanmin():
    arr = np.array([1, 2, np.nan, 3, np.nan, 4])
    result = nanops.nanmin(arr)
    assert result == 1

def test_nanmax():
    arr = np.array([1, 2, np.nan, 3, np.nan, 4])
    result = nanops.nanmax(arr)
    assert result == 4

def test_nanargmin():
    arr = np.array([1, 2, np.nan, 3, np.nan, 4])
    result = nanops.nanargmin(arr)
    assert result == 0

def test_nanargmax():
    arr = np.array([1, 2, np.nan, 3, np.nan, 4])
    result = nanops.nanargmax(arr)
    assert result == 5

def test_nansum():
    arr = np.array([1, 2, np.nan, 3, np.nan, 4])
    result = nanops.nansum(arr)
    assert result == 10

def test_nanmean():
    arr = np.array([1, 2, np.nan, 3, np.nan, 4])
    result = nanops.nanmean(arr)
    assert result == 2.5

def test_nanmedian():
    arr = np.array([1, 2, np.nan, 3, np.nan, 4])
    result = nanops.nanmedian(arr)
    assert result == 2.5

def test_nanvar():
    arr = np.array([1, 2, np.nan, 3, np.nan, 4])
    result = nanops.nanvar(arr)
    assert result == 1.6666666666666667

def test_nanstd():
    arr = np.array([1, 2, np.nan, 3, np.nan, 4])
    result = nanops.nanstd(arr)
    assert result == 1.2909944487358056

def test_nanprod():
    arr = np.array([1, 2, np.nan, 3, np.nan, 4])
    result = nanops.nanprod(arr)
    assert result == 24

def test_nancumsum():
    arr = np.array([1, 2, np.nan, 3, np.nan, 4])
    result = nanops.nancumsum(arr)
    assert (result == np.array([1, 3, 3, 6, 6, 10])).all()

def test_nancumprod():
    arr = np.array([1, 2, np.nan, 3, np.nan, 4])
    result = nanops.nancumprod(arr)
    assert (result == np.array([1, 2, 2, 6, 6, 24])).all()