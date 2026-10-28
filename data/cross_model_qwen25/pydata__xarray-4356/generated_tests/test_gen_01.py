import pytest
import numpy as np
import xarray.core.nanops as nanops

# Test _replace_nan function
def test_replace_nan():
    a = np.array([1, np.nan, 3])
    val = 0
    result, mask = nanops._replace_nan(a, val)
    assert np.array_equal(result, [1, 0, 3])
    assert np.array_equal(mask, [False, True, False])

def test_replace_nan_all_nan():
    a = np.array([np.nan, np.nan, np.nan])
    val = 0
    result, mask = nanops._replace_nan(a, val)
    assert np.array_equal(result, [0, 0, 0])
    assert np.array_equal(mask, [True, True, True])

def test_replace_nan_no_nan():
    a = np.array([1, 2, 3])
    val = 0
    result, mask = nanops._replace_nan(a, val)
    assert np.array_equal(result, [1, 2, 3])
    assert np.array_equal(mask, [False, False, False])

# Test _maybe_null_out function
def test_maybe_null_out():
    a = np.array([1, np.nan, 3])
    mask = np.array([False, True, False])
    result = nanops._maybe_null_out(a, 0, mask)
    assert np.isnan(result[1])

def test_maybe_null_out_all_nan():
    a = np.array([np.nan, np.nan, np.nan])
    mask = np.array([True, True, True])
    result = nanops._maybe_null_out(a, 0, mask)
    assert np.isnan(result)

# Test nanmin function
def test_nanmin():
    a = np.array([1, np.nan, 3])
    result = nanops.nanmin(a)
    assert result == 1

def test_nanmin_all_nan():
    a = np.array([np.nan, np.nan, np.nan])
    with pytest.raises(ValueError):
        nanops.nanmin(a)

# Test nanmax function
def test_nanmax():
    a = np.array([1, np.nan, 3])
    result = nanops.nanmax(a)
    assert result == 3

def test_nanmax_all_nan():
    a = np.array([np.nan, np.nan, np.nan])
    with pytest.raises(ValueError):
        nanops.nanmax(a)

# Test nanargmin function
def test_nanargmin():
    a = np.array([1, np.nan, 3])
    result = nanops.nanargmin(a)
    assert result == 0

def test_nanargmin_all_nan():
    a = np.array([np.nan, np.nan, np.nan])
    with pytest.raises(ValueError):
        nanops.nanargmin(a)

# Test nanargmax function
def test_nanargmax():
    a = np.array([1, np.nan, 3])
    result = nanops.nanargmax(a)
    assert result == 2

def test_nanargmax_all_nan():
    a = np.array([np.nan, np.nan, np.nan])
    with pytest.raises(ValueError):
        nanops.nanargmax(a)

# Test nansum function
def test_nansum():
    a = np.array([1, np.nan, 3])
    result = nanops.nansum(a)
    assert result == 4

def test_nansum_all_nan():
    a = np.array([np.nan, np.nan, np.nan])
    result = nanops.nansum(a)
    assert np.isnan(result)

# Test nanmean function
def test_nanmean():
    a = np.array([1, np.nan, 3])
    result = nanops.nanmean(a)
    assert result == 2

def test_nanmean_all_nan():
    a = np.array([np.nan, np.nan, np.nan])
    result = nanops.nanmean(a)
    assert np.isnan(result)

# Test nanmedian function
def test_nanmedian():
    a = np.array([1, np.nan, 3])
    result = nanops.nanmedian(a)
    assert result == 2

def test_nanmedian_all_nan():
    a = np.array([np.nan, np.nan, np.nan])
    result = nanops.nanmedian(a)
    assert np.isnan(result)

# Test nanvar function
def test_nanvar():
    a = np.array([1, np.nan, 3])
    result = nanops.nanvar(a)
    assert result == 1

def test_nanvar_all_nan():
    a = np.array([np.nan, np.nan, np.nan])
    result = nanops.nanvar(a)
    assert np.isnan(result)

# Test nanstd function
def test_nanstd():
    a = np.array([1, np.nan, 3])
    result = nanops.nanstd(a)
    assert result == 1

def test_nanstd_all_nan():
    a = np.array([np.nan, np.nan, np.nan])
    result = nanops.nanstd(a)
    assert np.isnan(result)

# Test nanprod function
def test_nanprod():
    a = np.array([1, np.nan, 3])
    result = nanops.nanprod(a)
    assert result == 3

def test_nanprod_all_nan():
    a = np.array([np.nan, np.nan, np.nan])
    result = nanops.nanprod(a)
    assert np.isnan(result)

# Test nancumsum function
def test_nancumsum():
    a = np.array([1, np.nan, 3])
    result = nanops.nancumsum(a)
    assert np.array_equal(result, [1, 1, 4])

def test_nancumsum_all_nan():
    a = np.array([np.nan, np.nan, np.nan])
    result = nanops.nancumsum(a)
    assert np.array_equal(result, [np.nan, np.nan, np.nan])

# Test nancumprod function
def test_nancumprod():
    a = np.array([1, np.nan, 3])
    result = nanops.nancumprod(a)
    assert np.array_equal(result, [1, 1, 3])

def test_nancumprod_all_nan():
    a = np.array([np.nan, np.nan, np.nan])
    result = nanops.nancumprod(a)
    assert np.array_equal(result, [np.nan, np.nan, np.nan])