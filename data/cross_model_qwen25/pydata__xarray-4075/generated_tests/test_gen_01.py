import numpy as np
import xarray as xr
import pytest

def test_weighted_init_with_dataarray():
    da = xr.DataArray(np.random.rand(3, 3))
    weights = xr.DataArray(np.random.rand(3, 3))
    weighted = Weighted(da, weights)
    assert isinstance(weighted, Weighted)

def test_weighted_init_with_dataset():
    ds = xr.Dataset({'var': xr.DataArray(np.random.rand(3, 3))})
    weights = xr.DataArray(np.random.rand(3, 3))
    weighted = Weighted(ds, weights)
    assert isinstance(weighted, Weighted)

def test_weighted_sum_of_weights():
    da = xr.DataArray(np.random.rand(3, 3))
    weights = xr.DataArray(np.random.rand(3, 3))
    weighted = Weighted(da, weights)
    result = weighted.sum_of_weights()
    assert isinstance(result, xr.DataArray)
    assert not result.isnull().any()

def test_weighted_sum():
    da = xr.DataArray(np.random.rand(3, 3))
    weights = xr.DataArray(np.random.rand(3, 3))
    weighted = Weighted(da, weights)
    result = weighted.sum()
    assert isinstance(result, xr.DataArray)
    assert not result.isnull().any()

def test_weighted_mean():
    da = xr.DataArray(np.random.rand(3, 3))
    weights = xr.DataArray(np.random.rand(3, 3))
    weighted = Weighted(da, weights)
    result = weighted.mean()
    assert isinstance(result, xr.DataArray)
    assert not result.isnull().any()

def test_weighted_with_missing_weights():
    da = xr.DataArray(np.random.rand(3, 3))
    weights = xr.DataArray(np.random.rand(3, 3))
    weights[0, 0] = np.nan
    with pytest.raises(ValueError):
        Weighted(da, weights)

def test_weighted_with_zero_sum_of_weights():
    da = xr.DataArray(np.random.rand(3, 3))
    weights = xr.DataArray(np.random.rand(3, 3))
    weights = weights.where(weights != 0, 0)  # Set some weights to 0 to make the sum 0
    weighted = Weighted(da, weights)
    result = weighted.mean()
    assert np.isnan(result.item())

def test_weighted_with_zero_weights():
    da = xr.DataArray(np.random.rand(3, 3))
    weights = xr.DataArray(np.zeros((3, 3)))
    weighted = Weighted(da, weights)
    result = weighted.mean()
    assert np.isnan(result.item())

def test_weighted_with_zero_weights_sum_of_weights():
    da = xr.DataArray(np.random.rand(3, 3))
    weights = xr.DataArray(np.zeros((3, 3)))
    weighted = Weighted(da, weights)
    result = weighted.sum_of_weights()
    assert np.isnan(result.item())

def test_weighted_keep_attrs():
    da = xr.DataArray(np.random.rand(3, 3), attrs={'units': 'm'})
    weights = xr.DataArray(np.random.rand(3, 3))
    weighted = Weighted(da, weights)
    result = weighted.mean(keep_attrs=True)
    assert result.attrs == {'units': 'm'}

def test_weighted_sum_of_weights_keep_attrs():
    da = xr.DataArray(np.random.rand(3, 3), attrs={'units': 'm'})
    weights = xr.DataArray(np.random.rand(3, 3))
    weighted = Weighted(da, weights)
    result = weighted.sum_of_weights(keep_attrs=True)
    assert result.attrs == {'units': 'm'}