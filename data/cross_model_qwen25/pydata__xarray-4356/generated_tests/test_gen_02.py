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

@pytest.mark.parametrize("dtype", [np.float64, np.float32, np.int32])
def test_replace_nan(dtype):
    a = np.array([1.0, np.nan, 3.0], dtype=dtype)
    val = 0
    result, mask = _replace_nan(a, val)
    assert np.allclose(result, [1.0, 0, 3.0])
    assert np.array_equal(mask, [False, True, False])

@pytest.mark.parametrize("dtype", [np.float64, np.float32, np.int32])
def test_maybe_null_out(dtype):
    a = np.array([1.0, np.nan, 3.0], dtype=dtype)
    axis = 0
    mask = np.array([False, True, False])
    result = _maybe_null_out(a, axis, mask, min_count=1)
    assert np.isnan(result)

@pytest.mark.parametrize("func", ["min", "max"])
def test_nan_minmax_object(func):
    a = np.array([1.0, np.nan, 3.0], dtype=np.float64)
    fill_value = np.inf if func == "min" else -np.inf
    result = _nan_minmax_object(func, fill_value, a)
    assert result == 1.0

@pytest.mark.parametrize("func", ["argmin", "argmax"])
def test_nan_argminmax_object(func):
    a = np.array([1.0, np.nan, 3.0], dtype=np.float64)
    fill_value = np.inf if func == "argmin" else -np.inf
    result = _nan_argminmax_object(func, fill_value, a)
    assert result == 0

def test_nanmin():
    a = np.array([1.0, np.nan, 3.0], dtype=np.float64)
    result = nanmin(a)
    assert result == 1.0

def test_nanmax():
    a = np.array([1.0, np.nan, 3.0], dtype=np.float64)
    result = nanmax(a)
    assert result == 3.0

def test_nanargmin():
    a = np.array([1.0, np.nan, 3.0], dtype=np.float64)
    result = nanargmin(a)
    assert result == 0

def test_nanargmax():
    a = np.array([1.0, np.nan, 3.0], dtype=np.float64)
    result = nanargmax(a)
    assert result == 2

def test_nansum():
    a = np.array([1.0, np.nan, 3.0], dtype=np.float64)
    result = nansum(a)
    assert result == 4.0

def test_nanmean():
    a = np.array([1.0, np.nan, 3.0], dtype=np.float64)
    result = nanmean(a)
    assert result == 2.0

def test_nanmedian():
    a = np.array([1.0, np.nan, 3.0], dtype=np.float64)
    result = nanmedian(a)
    assert result == 2.0

def test_nanvar():
    a = np.array([1.0, np.nan, 3.0], dtype=np.float64)
    result = nanvar(a)
    assert result == 1.0

def test_nanstd():
    a = np.array([1.0, np.nan, 3.0], dtype=np.float64)
    result = nanstd(a)
    assert result == 1.0

def test_nanprod():
    a = np.array([1.0, np.nan, 3.0], dtype=np.float64)
    result = nanprod(a)
    assert result == 3.0

def test_nancumsum():
    a = np.array([1.0, np.nan, 3.0], dtype=np.float64)
    result = nancumsum(a)
    assert np.array_equal(result, [1.0, 1.0, 4.0])

def test_nancumprod():
    a = np.array([1.0, np.nan, 3.0], dtype=np.float64)
    result = nancumprod(a)
    assert np.array_equal(result, [1.0, 1.0, 3.0])

def test_min_count_error():
    a = np.array([np.nan, np.nan], dtype=np.float64)
    with pytest.raises(ValueError):
        nansum(a, min_count=1)