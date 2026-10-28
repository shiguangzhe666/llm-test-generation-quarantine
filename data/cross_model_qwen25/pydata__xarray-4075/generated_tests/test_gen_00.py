import pytest
from xarray import DataArray, Dataset
from xarray.core.weighted import Weighted, DataArrayWeighted, DatasetWeighted

# Test Weighted Initialization
def test_weighted_init_dataarray():
    weights = DataArray([1, 2, 3])
    da = DataArray([10, 20, 30])
    weighted = DataArrayWeighted(da, weights)
    assert weighted.obj.equals(da)
    assert weighted.weights.equals(weights)

def test_weighted_init_dataset():
    weights = DataArray([1, 2, 3])
    ds = Dataset({"a": weights})
    weighted = DatasetWeighted(ds, weights)
    assert all(weighted.obj.equals(ds[var]) for var in ds.data_vars)
    assert weighted.weights.equals(weights)

# Test sum_of_weights
def test_sum_of_weights_dataarray():
    weights = DataArray([1, 2, 3], dims=['x'])
    da = DataArray([10, 20, 30], dims=['x'])
    weighted = DataArrayWeighted(da, weights)
    result = weighted.sum_of_weights(dim='x')
    expected = DataArray([6], dims=[])
    assert result.equals(expected)

def test_sum_of_weights_dataset():
    weights = DataArray([1, 2, 3], dims=['x'])
    da = DataArray([10, 20, 30], dims=['x'])
    ds = Dataset({"a": da})
    weighted = DatasetWeighted(ds, weights)
    result = weighted.sum_of_weights(dim='x')
    expected = Dataset({"a": DataArray([6], dims=[])})
    assert result.equals(expected)

# Test sum
def test_sum_dataarray():
    weights = DataArray([1, 2, 3], dims=['x'])
    da = DataArray([10, 20, 30], dims=['x'])
    weighted = DataArrayWeighted(da, weights)
    result = weighted.sum(dim='x')
    expected = DataArray([70], dims=[])
    assert result.equals(expected)

def test_sum_dataset():
    weights = DataArray([1, 2, 3], dims=['x'])
    da = DataArray([10, 20, 30], dims=['x'])
    ds = Dataset({"a": da})
    weighted = DatasetWeighted(ds, weights)
    result = weighted.sum(dim='x')
    expected = Dataset({"a": DataArray([70], dims=[])})
    assert result.equals(expected)

# Test mean
def test_mean_dataarray():
    weights = DataArray([1, 2, 3], dims=['x'])
    da = DataArray([10, 20, 30], dims=['x'])
    weighted = DataArrayWeighted(da, weights)
    result = weighted.mean(dim='x')
    expected = DataArray([35.0 / 6], dims=[])
    assert result.equals(expected)

def test_mean_dataset():
    weights = DataArray([1, 2, 3], dims=['x'])
    da = DataArray([10, 20, 30], dims=['x'])
    ds = Dataset({"a": da})
    weighted = DatasetWeighted(ds, weights)
    result = weighted.mean(dim='x')
    expected = Dataset({"a": DataArray([35.0 / 6], dims=[])})
    assert result.equals(expected)

# Test error handling
def test_weighted_init_invalid_weights():
    weights = DataArray([1, 2, None], dims=['x'])
    da = DataArray([10, 20, 30], dims=['x'])
    with pytest.raises(ValueError, match="`weights` cannot contain missing values"):
        DataArrayWeighted(da, weights)

def test_sum_of_weights_invalid_weights():
    weights = DataArray([1, 2, None], dims=['x'])
    da = DataArray([10, 20, 30], dims=['x'])
    weighted = DataArrayWeighted(da, weights)
    with pytest.raises(ValueError, match="`weights` cannot contain missing values"):
        weighted.sum_of_weights(dim='x')

def test_sum_invalid_weights():
    weights = DataArray([1, 2, None], dims=['x'])
    da = DataArray([10, 20, 30], dims=['x'])
    weighted = DataArrayWeighted(da, weights)
    with pytest.raises(ValueError, match="`weights` cannot contain missing values"):
        weighted.sum(dim='x')

def test_mean_invalid_weights():
    weights = DataArray([1, 2, None], dims=['x'])
    da = DataArray([10, 20, 30], dims=['x'])
    weighted = DataArrayWeighted(da, weights)
    with pytest.raises(ValueError, match="`weights` cannot contain missing values"):
        weighted.mean(dim='x')

# Test keep_attrs
def test_sum_of_weights_keep_attrs_dataarray():
    weights = DataArray([1, 2, 3], dims=['x'])
    da = DataArray([10, 20, 30], dims=['x'], attrs={"attr1": "value1"})
    weighted = DataArrayWeighted(da, weights)
    result = weighted.sum_of_weights(dim='x', keep_attrs=True)
    expected = DataArray([6], dims=[], attrs={"attr1": "value1"})
    assert result.equals(expected)

def test_sum_of_weights_keep_attrs_dataset():
    weights = DataArray([1, 2, 3], dims=['x'])
    da = DataArray([10, 20, 30], dims=['x'], attrs={"attr1": "value1"})
    ds = Dataset({"a": da})
    weighted = DatasetWeighted(ds, weights)
    result = weighted.sum_of_weights(dim='x', keep_attrs=True)
    expected = Dataset({"a": DataArray([6], dims=[], attrs={"attr1": "value1"})})
    assert result.equals(expected)