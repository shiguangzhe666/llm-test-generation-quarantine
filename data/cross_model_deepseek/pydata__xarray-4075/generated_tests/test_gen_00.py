import pytest
import xarray as xr
import numpy as np

def test_weighted_init():
    da = xr.DataArray([1, 2, 3])
    weights = xr.DataArray([1, 2, 3])
    weighted = da.weighted(weights)
    assert weighted.obj is da
    assert weighted.weights is weights

def test_weighted_init_invalid_weights():
    da = xr.DataArray([1, 2, 3])
    weights = xr.DataArray([1, 2, None])
    with pytest.raises(ValueError):
        weighted = da.weighted(weights)

def test_weighted_sum_of_weights():
    da = xr.DataArray([1, 2, 3])
    weights = xr.DataArray([1, 2, 3])
    weighted = da.weighted(weights)
    assert weighted.sum_of_weights().equals(weights.sum())

def test_weighted_sum():
    da = xr.DataArray([1, 2, 3])
    weights = xr.DataArray([1, 2, 3])
    weighted = da.weighted(weights)
    assert weighted.sum().equals(da.sum() * weights.sum())

def test_weighted_mean():
    da = xr.DataArray([1, 2, 3])
    weights = xr.DataArray([1, 2, 3])
    weighted = da.weighted(weights)
    assert weighted.mean().equals(da.mean() * weights.sum())

def test_weighted_reduce_skipna():
    da = xr.DataArray([1, 2, np.nan])
    weights = xr.DataArray([1, 2, 3])
    weighted = da.weighted(weights)
    assert weighted.sum(skipna=True).equals(da.fillna(0).sum() * weights.sum())

def test_weighted_reduce_keep_attrs():
    da = xr.DataArray([1, 2, 3], attrs={'units': 'm'})
    weights = xr.DataArray([1, 2, 3])
    weighted = da.weighted(weights)
    reduced = weighted.sum(keep_attrs=True)
    assert reduced.equals(da.sum() * weights.sum())
    assert reduced.attrs == da.attrs

def test_weighted_reduce_dim():
    da = xr.DataArray([[1, 2], [3, 4]])
    weights = xr.DataArray([1, 2])
    weighted = da.weighted(weights)
    assert weighted.sum(dim='dim0').equals(da.sum(dim='dim0') * weights.sum())

def test_weighted_mean_dim():
    da = xr.DataArray([[1, 2], [3, 4]])
    weights = xr.DataArray([1, 2])
    weighted = da.weighted(weights)
    assert weighted.mean(dim='dim0').equals(da.mean(dim='dim0') * weights.sum())

def test_weighted_sum_of_weights_dim():
    da = xr.DataArray([[1, 2], [3, 4]])
    weights = xr.DataArray([1, 2])
    weighted = da.weighted(weights)
    assert weighted.sum_of_weights(dim='dim0').equals(weights.sum() * da.shape[1])