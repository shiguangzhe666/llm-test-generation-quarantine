import pytest
import numpy as np
import xarray as xr
from xarray.core.weighted import Weighted, DataArrayWeighted, DatasetWeighted
from xarray.core.dataarray import DataArray
from xarray.core.dataset import Dataset
from xarray.core.computation import dot
from xarray.core.options import _get_keep_attrs

def test_weighted_init_valid_dataarray():
    da = DataArray(np.random.rand(3, 4))
    weights = DataArray(np.random.rand(3, 4))
    weighted = Weighted(da, weights)
    assert weighted.obj is da
    assert weighted.weights is weights

def test_weighted_init_valid_dataset():
    ds = Dataset({"a": np.random.rand(3, 4)})
    weights = DataArray(np.random.rand(3, 4))
    weighted = Weighted(ds, weights)
    assert weighted.obj is ds
    assert weighted.weights is weights

def test_weighted_init_invalid_weights_type():
    da = DataArray(np.random.rand(3, 4))
    with pytest.raises(ValueError, match=r"`weights` must be a DataArray"):
        Weighted(da, np.random.rand(3, 4))

def test_weighted_init_weights_with_missing_values():
    da = DataArray(np.random.rand(3, 4))
    weights = DataArray(np.random.rand(3, 4))
    weights[0, 0] = np.nan
    with pytest.raises(ValueError, match=r"`weights` cannot contain missing values"):
        Weighted(da, weights)

def test_weighted_reduce_skipna_true():
    da = DataArray(np.array([[1.0, 2.0], [3.0, 4.0]]))
    weights = DataArray(np.array([[1.0, 2.0], [3.0, 4.0]]))
    result = Weighted._reduce(da, weights, dim="dim0", skipna=True)
    expected = dot(da, weights, dims="dim0")
    assert np.allclose(result.values, expected.values)

def test_weighted_reduce_skipna_false():
    da = DataArray(np.array([[1.0, 2.0], [3.0, 4.0]]))
    weights = DataArray(np.array([[1.0, 2.0], [3.0, 4.0]]))
    result = Weighted._reduce(da, weights, dim="dim0", skipna=False)
    expected = dot(da, weights, dims="dim0")
    assert np.allclose(result.values, expected.values)

def test_weighted_sum_of_weights_masking():
    da = DataArray(np.array([[1.0, 2.0], [3.0, 4.0]]))
    weights = DataArray(np.array([[1.0, 2.0], [3.0, 4.0]]))
    result = Weighted._sum_of_weights(da, dim="dim0")
    expected = np.array([4.0, 7.0])
    assert np.allclose(result.values, expected)

def test_weighted_sum_of_weights_with_nan():
    da = DataArray(np.array([[1.0, 2.0], [3.0, np.nan]]))
    weights = DataArray(np.array([[1.0, 2.0], [3.0, 4.0]]))
    result = Weighted._sum_of_weights(da, dim="dim0")
    expected = np.array([4.0, 7.0])
    assert np.allclose(result.values, expected)

def test_weighted_weighted_sum():
    da = DataArray(np.array([[1.0, 2.0], [3.0, 4.0]]))
    weights = DataArray(np.array([[1.0, 2.0], [3.0, 4.0]]))
    result = Weighted._weighted_sum(da, dim="dim0")
    expected = np.array([4.0, 7.0])
    assert np.allclose(result.values, expected)

def test_weighted_weighted_mean():
    da = DataArray(np.array([[1.0, 2.0], [3.0, 4.0]]))
    weights = DataArray(np.array([[1.0, 2.0], [3.0, 4.0]]))
    result = Weighted._weighted_mean(da, dim="dim0")
    expected = np.array([4.0 / 4.0, 7.0 / 7.0])
    assert np.allclose(result.values, expected)

def test_weighted_weighted_mean_zero_sum():
    da = DataArray(np.array([[1.0, 2.0], [3.0, 4.0]]))
    weights = DataArray(np.array([[0.0, 0.0], [0.0, 0.0]]))
    result = Weighted._weighted_mean(da, dim="dim0")
    expected = np.array([np.nan, np.nan])
    assert np.allclose(result.values, expected)

def test_dataarray_weighted_implementation_keep_attrs_true():
    da = DataArray(np.random.rand(3, 4), attrs={"attr1": "value1"})
    weighted = DataArrayWeighted(da, DataArray(np.random.rand(3, 4)))
    result = weighted._implementation(weighted._weighted_sum, dim="dim0", keep_attrs=True)
    assert result.attrs == da.attrs

def test_dataarray_weighted_implementation_keep_attrs_false():
    da = DataArray(np.random.rand(3, 4), attrs={"attr1": "value1"})
    weighted = DataArrayWeighted(da, DataArray(np.random.rand(3, 4)))
    result = weighted._implementation(weighted._weighted_sum, dim="dim0", keep_attrs=False)
    assert "attr1" not in result.attrs

def test_dataset_weighted_implementation():
    ds = Dataset({"a": np.random.rand(3, 4)}, attrs={"attr1": "value1"})
    weighted = DatasetWeighted(ds, DataArray(np.random.rand(3, 4)))
    result = weighted._implementation(weighted._weighted_sum, dim="dim0")
    assert "attr1" in result.attrs

def test_dataset_weighted_implementation_no_attrs():
    ds = Dataset({"a": np.random.rand(3, 4)})
    weighted = DatasetWeighted(ds, DataArray(np.random.rand(3, 4)))
    result = weighted._implementation(weighted._weighted_sum, dim="dim0")
    assert "attrs" not in result.attrs