import pytest
from xarray import DataArray, Dataset
from xarray.core.weighted import Weighted, DataArrayWeighted, DatasetWeighted

# Test DataArrayWeighted
def test_dataarray_weighted_init():
    weights = DataArray([1, 2, 3])
    da = DataArray([10, 20, 30])
    weighted = DataArrayWeighted(da, weights)
    assert weighted.obj.equals(da)
    assert weighted.weights.equals(weights)

def test_dataarray_weighted_sum():
    weights = DataArray([1, 2, 3])
    da = DataArray([10, 20, 30])
    weighted = DataArrayWeighted(da, weights)
    result = weighted.sum()
    expected = DataArray([10, 40, 90])
    assert result.equals(expected)

def test_dataarray_weighted_mean():
    weights = DataArray([1, 2, 3])
    da = DataArray([10, 20, 30])
    weighted = DataArrayWeighted(da, weights)
    result = weighted.mean()
    expected = DataArray([10, 20, 30]) / DataArray([1, 2, 3])
    assert result.equals(expected)

def test_dataarray_weighted_sum_of_weights():
    weights = DataArray([1, 2, 3])
    da = DataArray([10, 20, 30])
    weighted = DataArrayWeighted(da, weights)
    result = weighted.sum_of_weights()
    expected = DataArray([1, 2, 3])
    assert result.equals(expected)

# Test DatasetWeighted
def test_dataset_weighted_init():
    weights = DataArray([1, 2, 3])
    ds = Dataset({"a": DataArray([10, 20, 30])})
    weighted = DatasetWeighted(ds, weights)
    assert weighted.obj.equals(ds)
    assert weighted.weights.equals(weights)

def test_dataset_weighted_sum():
    weights = DataArray([1, 2, 3])
    ds = Dataset({"a": DataArray([10, 20, 30])})
    weighted = DatasetWeighted(ds, weights)
    result = weighted.sum()
    expected = Dataset({"a": DataArray([10, 40, 90])})
    assert result.equals(expected)

def test_dataset_weighted_mean():
    weights = DataArray([1, 2, 3])
    ds = Dataset({"a": DataArray([10, 20, 30])})
    weighted = DatasetWeighted(ds, weights)
    result = weighted.mean()
    expected = Dataset({"a": DataArray([10, 20, 30]) / DataArray([1, 2, 3])})
    assert result.equals(expected)

def test_dataset_weighted_sum_of_weights():
    weights = DataArray([1, 2, 3])
    ds = Dataset({"a": DataArray([10, 20, 30])})
    weighted = DatasetWeighted(ds, weights)
    result = weighted.sum_of_weights()
    expected = Dataset({"a": DataArray([1, 2, 3])})
    assert result.equals(expected)

# Edge cases and boundary conditions
def test_dataarray_weighted_sum_with_empty_weights():
    weights = DataArray([0, 0, 0])
    da = DataArray([10, 20, 30])
    with pytest.raises(ValueError, match="Weights sum to 0.0 along the reduced dimension"):
        DataArrayWeighted(da, weights).sum()

def test_dataarray_weighted_mean_with_zero_sum_weights():
    weights = DataArray([0, 0, 0])
    da = DataArray([10, 20, 30])
    with pytest.raises(ValueError, match="Weights sum to 0.0 along the reduced dimension"):
        DataArrayWeighted(da, weights).mean()

def test_dataarray_weighted_sum_of_weights_with_zero_sum_weights():
    weights = DataArray([0, 0, 0])
    da = DataArray([10, 20, 30])
    result = DataArrayWeighted(da, weights).sum_of_weights()
    assert result.equals(DataArray([0, 0, 0]))

def test_dataarray_weighted_mean_with_missing_values():
    weights = DataArray([1, 2, 3])
    da = DataArray([10, 20, 30], mask=[True, False, False])
    with pytest.raises(ValueError, match="Missing values in data"):
        DataArrayWeighted(da, weights).mean()

def test_dataarray_weighted_sum_of_weights_with_missing_values():
    weights = DataArray([1, 2, 3])
    da = DataArray([10, 20, 30], mask=[True, False, False])
    result = DataArrayWeighted(da, weights).sum_of_weights()
    assert result.equals(DataArray([1, 2, 3], mask=[True, False, False]))

def test_dataset_weighted_sum_with_empty_weights():
    weights = DataArray([0, 0, 0])
    ds = Dataset({"a": DataArray([10, 20, 30])})
    with pytest.raises(ValueError, match="Weights sum to 0.0 along the reduced dimension"):
        DatasetWeighted(ds, weights).sum()

def test_dataset_weighted_mean_with_zero_sum_weights():
    weights = DataArray([0, 0, 0])
    ds = Dataset({"a": DataArray([10, 20, 30])})
    with pytest.raises(ValueError, match="Weights sum to 0.0 along the reduced dimension"):
        DatasetWeighted(ds, weights).mean()

def test_dataset_weighted_sum_of_weights_with_zero_sum_weights():
    weights = DataArray([0, 0, 0])
    ds = Dataset({"a": DataArray([10, 20, 30])})
    result = DatasetWeighted(ds, weights).sum_of_weights()
    assert result.equals(Dataset({"a": DataArray([0, 0, 0])}))

def test_dataset_weighted_mean_with_missing_values():
    weights = DataArray([1, 2, 3])
    ds = Dataset({"a": DataArray([10, 20, 30], mask=[True, False, False])})
    with pytest.raises(ValueError, match="Missing values in data"):
        DatasetWeighted(ds, weights).mean()

def test_dataset_weighted_sum_of_weights_with_missing_values():
    weights = DataArray([1, 2, 3])
    ds = Dataset({"a": DataArray([10, 20, 30], mask=[True, False, False])})
    result = DatasetWeighted(ds, weights).sum_of_weights()
    assert result.equals(Dataset({"a": DataArray([1, 2, 3], mask=[True, False, False])}))