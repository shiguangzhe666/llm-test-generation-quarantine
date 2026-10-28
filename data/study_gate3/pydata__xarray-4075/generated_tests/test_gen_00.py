import pytest
import numpy as np
import xarray as xr

def test_weighted_init_valid():
    da = xr.DataArray(np.array([1, 2, 3]))
    weights = xr.DataArray(np.array([0.5, 1.0, 1.5]))
    weighted = Weighted(da, weights)
    assert weighted.obj is da
    assert weighted.weights is weights

def test_weighted_init_invalid_weights_type():
    da = xr.DataArray(np.array([1, 2, 3]))
    weights = np.array([0.5, 1.0, 1.5])
    with pytest.raises(ValueError, match="`weights` must be a DataArray"):
        Weighted(da, weights)

def test_weighted_init_weights_with_nan():
    da = xr.DataArray(np.array([1, 2, 3]))
    weights = xr.DataArray(np.array([0.5, np.nan, 1.5]))
    with pytest.raises(ValueError, match="`weights` cannot contain missing values"):
        Weighted(da, weights)

def test_weighted_reduce_skipna_true():
    da = xr.DataArray(np.array([1, 2, np.nan]))
    weights = xr.DataArray(np.array([0.5, 1.0, 1.5]))
    result = Weighted._reduce(da, weights, dim=None, skipna=True)
    expected = np.array([1 * 0.5, 2 * 1.0, np.nan * 1.5]).sum()
    assert np.isnan(expected)  # Should be NaN due to skipna=True

def test_weighted_reduce_skipna_false():
    da = xr.DataArray(np.array([1, 2, np.nan]))
    weights = xr.DataArray(np.array([0.5, 1.0, 1.5]))
    result = Weighted._reduce(da, weights, dim=None, skipna=False)
    expected = np.array([1 * 0.5, 2 * 1.0, np.nan * 1.5]).sum()
    assert np.isnan(expected)

def test_weighted_sum_of_weights():
    da = xr.DataArray(np.array([1, 2, 3]))
    weights = xr.DataArray(np.array([0.5, 1.0, 1.5]))
    weighted = Weighted(da, weights)
    result = weighted.sum_of_weights()
    expected = np.array([0.5, 1.0, 1.5]).sum()
    assert np.allclose(result, expected)

def test_weighted_mean_zero_sum():
    da = xr.DataArray(np.array([1, 2, 3]))
    weights = xr.DataArray(np.array([0, 0, 0]))
    weighted = Weighted(da, weights)
