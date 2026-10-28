import numpy as np
import pytest
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

@pytest.mark.parametrize("dtype", [np.float64, np.float32, np.int64, np.int32, np.object])
def test_replace_nan(dtype):
    arr = np.array([1, 2, np.nan, 4], dtype=dtype)
    expected_val = np.array([1, 2, 0, 4], dtype=dtype)
    expected_mask = np.array([False, False, True, False], dtype=bool)
    result, mask = _replace_nan(arr, 0)
    assert np.array_equal(result, expected_val)
    assert np.array_equal(mask, expected_mask)

@pytest.mark.parametrize("dtype", [np.float64, np.float32, np.int64, np.int32, np.object])
def test_maybe_null_out(dtype):
    arr = np.array([1, 2, np.nan, 4], dtype=dtype)
    mask = np.array([False, False, True, False], dtype=bool)
    result = _maybe_null_out(arr, 0, mask, min_count=2)
    if dtype.kind == "O":
        assert np.isnan(result)
    else:
        assert result == 0

@pytest.mark.parametrize("dtype", [np.float64, np.float32, np.int64, np.int32, np.object])
def test_nanmin(dtype):
    arr = np.array([1, 2, np.nan, 4], dtype=dtype)
    result = nanmin(arr)
    if dtype.kind == "O":
        assert np.isnan(result)
    else:
        assert result == 1

@pytest.mark.parametrize("dtype", [np.float64, np.float32, np.int64, np.int32, np.object])
def test_nanmax(dtype):
    arr = np.array([1, 2, np.nan, 4], dtype=dtype)
    result = nanmax(arr)
    if dtype.kind == "O":
        assert np.isnan(result)
    else:
        assert result == 4

@pytest.mark.parametrize("dtype", [np.float64, np.float32, np.int64, np.int32, np.object])
def test_nanargmin(dtype):
    arr = np.array([1, 2, np.nan, 4], dtype=dtype)
    result = nanargmin(arr)
    if dtype.kind == "O":
        assert result == 0
    else:
        assert result == 0

@pytest.mark.parametrize("dtype", [np.float64, np.float32, np.int64, np.int32, np.object])
def test_nanargmax(dtype):
    arr = np.array([1, 2, np.nan, 4], dtype=dtype)
    result = nanargmax(arr)
    if dtype.kind == "O":
        assert result == 3
    else:
        assert result == 3

@pytest.mark.parametrize("dtype", [np.float64, np.float32, np.int64, np.int32, np.object])
def test_nansum(dtype):
    arr = np.array([1, 2, np.nan, 4], dtype=dtype)
    result = nansum(arr)
    if dtype.kind == "O":
        assert np.isnan(result)
    else:
        assert result == 7

@pytest.mark.parametrize("dtype", [np.float64, np.float32, np.int64, np.int32, np.object])
def test_nanmean(dtype):
    arr = np.array([1, 2, np.nan, 4], dtype=dtype)
    result = nanmean(arr)
    if dtype.kind == "O":
        assert np.isnan(result)
    else:
        assert result == 2.5

@pytest.mark.parametrize("dtype", [np.float64, np.float32, np.int64, np.int32, np.object])
def test_nanmedian(dtype):
    arr = np.array([1, 2, np.nan, 4], dtype=dtype)
    result = nanmedian(arr)
    if dtype.kind == "O":
        assert np.isnan(result)
    else:
        assert result == 2.5

@pytest.mark.parametrize("dtype", [np.float64, np.float32, np.int64, np.int32, np.object])
def test_nanvar(dtype):
    arr = np.array([1, 2, np.nan, 4], dtype=dtype)
    result = nanvar(arr)
    if dtype.kind == "O":
        assert np.isnan(result)
    else:
        assert result == 2.25

@pytest.mark.parametrize("dtype", [np.float64, np.float32, np.int64, np.int32, np.object])
def test_nanstd(dtype):
    arr = np.array([1, 2, np.nan, 4], dtype=dtype)
    result = nanstd(arr)
    if dtype.kind == "O":
        assert np.isnan(result)
    else:
        assert result == 1.5

@pytest.mark.parametrize("dtype", [np.float64, np.float32, np.int64, np.int32, np.object])
def test_nanprod(dtype):
    arr = np.array([1, 2, np.nan, 4], dtype=dtype)
    result = nanprod(arr)
    if dtype.kind == "O":
        assert np.isnan(result)
    else:
        assert result == 8

@pytest.mark.parametrize("dtype", [np.float64, np.float32, np.int64, np.int32, np.object])
def test_nancumsum(dtype):
    arr = np.array([1, 2, np.nan, 4], dtype=dtype)
    result = nancumsum(arr)
    if dtype.kind == "O":
        assert np.array_equal(result, [1, 3, 3, 7])
    else:
        assert np.array_equal(result, [1, 3, 3, 7])

@pytest.mark.parametrize("dtype", [np.float64, np.float32, np.int64, np.int32, np.object])
def test_nancumprod(dtype):
    arr = np.array([1, 2, np.nan, 4], dtype=dtype)
    result = nancumprod(arr)
    if dtype.kind == "O":
        assert np.array_equal(result, [1, 2, 2, 8])
    else:
        assert np.array_equal(result, [1, 2, 2, 8])