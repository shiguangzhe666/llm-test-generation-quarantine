import pytest
from xarray.core.weighted import Weighted
from xarray.core.computation import dot
from xarray.core.options import _get_keep_attrs
from xarray.dataarray import DataArray
from xarray.dataset import Dataset

def test_weighted_sum_of_weights():
    obj = DataArray([1, 2, 3, 4], dims=['x'])
    weights = DataArray([1, 2, 3, 4], dims=['x'])
    weighted = Weighted(obj, weights)
    sum_of_weights = weighted.sum_of_weights()
    assert sum_of_weights.data == [10]

def test_weighted_sum():
    obj = DataArray([1, 2, 3, 4], dims=['x'])
    weights = DataArray([1, 2, 3, 4], dims=['x'])
    weighted = Weighted(obj, weights)
    sum = weighted.sum()
    assert sum.data == [10]

def test_weighted_mean():
    obj = DataArray([1, 2, 3, 4], dims=['x'])
    weights = DataArray([1, 2, 3, 4], dims=['x'])
    weighted = Weighted(obj, weights)
    mean = weighted.mean()
    assert mean.data == [2.5]

def test_weighted_sum_of_weights_with_dim():
    obj = DataArray([1, 2, 3, 4], dims=['x'])
    weights = DataArray([1, 2, 3, 4], dims=['x'])
    weighted = Weighted(obj, weights)
    sum_of_weights = weighted.sum_of_weights(dim='x')
    assert sum_of_weights.data == [10]

def test_weighted_sum_with_dim():
    obj = DataArray([1, 2, 3, 4], dims=['x'])
    weights = DataArray([1, 2, 3, 4], dims=['x'])
    weighted = Weighted(obj, weights)
    sum = weighted.sum(dim='x')
    assert sum.data == [10]

def test_weighted_mean_with_dim():
    obj = DataArray([1, 2, 3, 4], dims=['x'])
    weights = DataArray([1, 2, 3, 4], dims=['x'])
    weighted = Weighted(obj, weights)
    mean = weighted.mean(dim='x')
    assert mean.data == [2.5]

def test_weighted_sum_with_keep_attrs():
    obj = DataArray([1, 2, 3, 4], dims=['x'])
    weights = DataArray([1, 2, 3, 4], dims=['x'])
    weighted = Weighted(obj, weights)
    sum = weighted.sum(keep_attrs=True)
    assert sum.attrs == obj.attrs

def test_weighted_mean_with_keep_attrs():
    obj = DataArray([1, 2, 3, 4], dims=['x'])
    weights = DataArray([1, 2, 3, 4], dims=['x'])
    weighted = Weighted(obj, weights)
    mean = weighted.mean(keep_attrs=True)
    assert mean.attrs == obj.attrs

def test_weighted_sum_of_weights_with_missing_values():
    obj = DataArray([1, 2, 3, 4], dims=['x'])
    weights = DataArray([1, 2, 3, 4], dims=['x'])
    weights = weights.fillna(0.0)
    weighted = Weighted(obj, weights)
    sum_of_weights = weighted.sum_of_weights()
    assert sum_of_weights.data == [10]

def test_weighted_sum_with_missing_values():
    obj = DataArray([1, 2, 3, 4], dims=['x'])
    weights = DataArray([1, 2, 3, 4], dims=['x'])
    weights = weights.fillna(0.0)
    weighted = Weighted(obj, weights)
    sum = weighted.sum()
    assert sum.data == [10]

def test_weighted_mean_with_missing_values():
    obj = DataArray([1, 2, 3, 4], dims=['x'])
    weights = DataArray([1, 2, 3, 4], dims=['x'])
    weights = weights.fillna(0.0)
    weighted = Weighted(obj, weights)
    mean = weighted.mean()
    assert mean.data == [2.5]

def test_weighted_sum_with_multiple_dims():
    obj = DataArray([1, 2, 3, 4], dims=['x'])
    weights = DataArray([1, 2, 3, 4], dims=['x'])
    weighted = Weighted(obj, weights)
    sum = weighted.sum(dim=['x'])
    assert sum.data == [10]

def test_weighted_mean_with_multiple_dims():
    obj = DataArray([1, 2, 3, 4], dims=['x'])
    weights = DataArray([1, 2, 3, 4], dims=['x'])
    weighted = Weighted(obj, weights)
    mean = weighted.mean(dim=['x'])
    assert mean.data == [2.5]

def test_weighted_sum_with_dataset():
    obj = Dataset({'x': (['x'], [1, 2, 3, 4])})
    weights = Dataset({'x': (['x'], [1, 2, 3, 4])})
    weighted = Weighted(obj, weights)
    sum = weighted.sum()
    assert sum['x'].data == [10]

def test_weighted_mean_with_dataset():
    obj = Dataset({'x': (['x'], [1, 2, 3, 4])})
    weights = Dataset({'x': (['x'], [1, 2, 3, 4])})
    weighted = Weighted(obj, weights)
    mean = weighted.mean()
    assert mean['x'].data == [2.5]