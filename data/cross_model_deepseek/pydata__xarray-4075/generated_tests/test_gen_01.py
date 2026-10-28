import pytest
import xarray as xr
import numpy as np

def test_weighted_init():
    da = xr.DataArray([1, 2, 3, 4], dims='dim_0')
    weights = xr.DataArray([1, 2, 3, 4], dims='dim_0')
    weighted = da.weighted(weights)
    assert weighted.obj is da
    assert weighted.weights is weights

def test_weighted_init_with_missing_weights():
    da = xr.DataArray([1, 2, 3, 4], dims='dim_0')
    weights = xr.DataArray([1, 2, None, 4], dims='dim_0')
    with pytest.raises(ValueError, match="`weights` cannot contain missing values."):
        da.weighted(weights)

def test_weighted_init_with_non_dataarray_weights():
    da = xr.DataArray([1, 2, 3, 4], dims='dim_0')
    weights = [1, 2, 3, 4]
    with pytest.raises(ValueError, match="`weights` must be a DataArray"):
        da.weighted(weights)

def test_weighted_sum_of_weights():
    da = xr.DataArray([1, 2, 3, 4], dims='dim_0')
    weights = xr.DataArray([1, 2, 3, 4], dims='dim_0')
    weighted = da.weighted(weights)
    assert weighted.sum_of_weights().values == np.sum(weights * da)

def test_weighted_sum():
    da = xr.DataArray([1, 2, 3, 4], dims='dim_0')
    weights = xr.DataArray([1, 2, 3, 4], dims='dim_0')
    weighted = da.weighted(weights)
    assert weighted.sum().values == np.sum(weights * da)

def test_weighted_mean():
    da = xr.DataArray([1, 2, 3, 4], dims='dim_0')
    weights = xr.DataArray([1, 2, 3, 4], dims='dim_0')
    weighted = da.weighted(weights)
    assert weighted.mean().values == np.sum(weights * da) / np.sum(weights)