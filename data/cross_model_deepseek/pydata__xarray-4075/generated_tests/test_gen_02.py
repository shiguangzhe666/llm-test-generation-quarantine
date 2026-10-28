import pytest
import xarray as xr
import numpy as np

from xarray.core.weighted import DataArrayWeighted, DatasetWeighted

def test_weighted_sum_dataarray():
    da = xr.DataArray([1, 2, 3, 4], dims='x')
    weights = xr.DataArray([0.1, 0.2, 0.3, 0.4], dims='x')
    expected = sum([1 * 0.1, 2 * 0.2, 3 * 0.3, 4 * 0.4])
    result = DataArrayWeighted(da, weights).sum(dim='x')
    np.testing.assert_allclose(result, expected)

def test_weighted_sum_dataset():
    ds = xr.Dataset({'x': xr.DataArray([1, 2, 3, 4], dims='x')})
    weights = xr.DataArray([0.1, 0.2, 0.3, 0.4], dims='x')
    expected = sum([1 * 0.1, 2 * 0.2, 3 * 0.3, 4 * 0.4])
    result = ds.weighted(weights).sum(dim='x')
    np.testing.assert_allclose(result, expected)

def test_weighted_mean_dataarray():
    da = xr.DataArray([1, 2, 3, 4], dims='x')
    weights = xr.DataArray([0.1, 0.2, 0.3, 0.4], dims='x')
    expected = sum([1 * 0.1, 2 * 0.2, 3 * 0.3, 4 * 0.4]) / sum([0.1, 0.2, 0.3, 0.4])
    result = DataArrayWeighted(da, weights).mean(dim='x')
    np.testing.assert_allclose(result, expected)

def test_weighted_mean_dataset():
    ds = xr.Dataset({'x': xr.DataArray([1, 2, 3, 4], dims='x')})
    weights = xr.DataArray([0.1, 0.2, 0.3, 0.4], dims='x')
    expected = sum([1 * 0.1, 2 * 0.2, 3 * 0.3, 4 * 0.4]) / sum([0.1, 0.2, 0.3, 0.4])
    result = ds.weighted(weights).mean(dim='x')
    np.testing.assertclose(result, expected)

def test_sum_of_weights_dataarray():
    da = xr.DataArray([1, 2, 3, 4], dims='x')
    weights = xr.DataArray([0.1, 0.2, 0.3, 0.4], dims='x')
    expected = sum([0.1, 0.2, 0.3, 0.4])
    result = DataArrayWeighted(da, weights).sum_of_weights(dim='x')
    np.testing.assert_allclose(result, expected)

def test_sum_of_weights_dataset():
    ds = xr.Dataset({'x': xr.DataArray([1, 2, 3, 4], dims='x')})
    weights = xr.DataArray([0.1, 0.2, 0.3, 0.4], dims='x')
    expected = sum([0.1, 0.2, 0.3, 0.4])
    result = ds.weighted(weights).sum_of_weights(dim='x')
    np.testing.assert_allclose(result, expected)

def test_weighted_reduce_dataarray_skipna():
    da = xr.DataArray([1, 2, np.nan, 4], dims='x')
    weights = xr.DataArray([0.1, 0.2, 0.3, 0.4], dims='x')
    expected = sum([1 * 0.1, 2 * 0.2, 0, 4 * 0.4])
    result = DataArrayWeighted(da, weights).sum(dim='x', skipna=True)
    np.testing.assert_allclose(result, expected)

def test_weighted_reduce_dataset_skipna():
    ds = xr.Dataset({'x': xr.DataArray([1, 2, np.nan, 4], dims='x')})
    weights = xr.DataArray([0.1, 0.2, 0.3, 0.4], dims='x')
    expected = sum([1 * 0.1, 2 * 0.2, 0, 4 * 0.4])
    result = ds.weighted(weights).sum(dim='x', skipna=True)
    np.testing.assert_allclose(result, expected)