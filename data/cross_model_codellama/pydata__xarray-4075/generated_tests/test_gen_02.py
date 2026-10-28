import pytest
from xarray.core.weighted import DataArrayWeighted, DatasetWeighted

def test_weighted_sum_of_weights():
    da = DataArray([0, 1, 2, 3, 4], dims="x")
    weights = DataArray([1, 2, 3, 4, 5], dims="x")
    weighted = DataArrayWeighted(da, weights)
    sum_of_weights = weighted.sum_of_weights(dim="x")
    assert sum_of_weights.values.tolist() == [15]
    assert sum_of_weights.dims == ("x",)

def test_weighted_sum():
    da = DataArray([0, 1, 2, 3, 4], dims="x")
    weights = DataArray([1, 2, 3, 4, 5], dims="x")
    weighted = DataArrayWeighted(da, weights)
    sum = weighted.sum(dim="x")
    assert sum.values.tolist() == [10]
    assert sum.dims == ("x",)

def test_weighted_mean():
    da = DataArray([0, 1, 2, 3, 4], dims="x")
    weights = DataArray([1, 2, 3, 4, 5], dims="x")
    weighted = DataArrayWeighted(da, weights)
    mean = weighted.mean(dim="x")
    assert mean.values.tolist() == [2]
    assert mean.dims == ("x",)

def test_weighted_sum_of_weights_2d():
    da = DataArray([[0, 1], [2, 3]], dims=("x", "y"))
    weights = DataArray([[1, 2], [3, 4]], dims=("x", "y"))
    weighted = DataArrayWeighted(da, weights)
    sum_of_weights = weighted.sum_of_weights(dim=("x", "y"))
    assert sum_of_weights.values.tolist() == [[3, 6]]
    assert sum_of_weights.dims == ("x", "y")

def test_weighted_sum_2d():
    da = DataArray([[0, 1], [2, 3]], dims=("x", "y"))
    weights = DataArray([[1, 2], [3, 4]], dims=("x", "y"))
    weighted = DataArrayWeighted(da, weights)
    sum = weighted.sum(dim=("x", "y"))
    assert sum.values.tolist() == [[1, 3]]
    assert sum.dims == ("x", "y")

def test_weighted_mean_2d():
    da = DataArray([[0, 1], [2, 3]], dims=("x", "y"))
    weights = DataArray([[1, 2], [3, 4]], dims=("x", "y"))
    weighted = DataArrayWeighted(da, weights)
    mean = weighted.mean(dim=("x", "y"))
    assert mean.values.tolist() == [[0.5, 1.5]]
    assert mean.dims == ("x", "y")

def test_weighted_sum_of_weights_3d():
    da = DataArray([[[0, 1], [2, 3]], [[4, 5], [6, 7]]], dims=("x", "y", "z"))
    weights = DataArray([[[1, 2], [3, 4]], [[5, 6], [7, 8]]], dims=("x", "y", "z"))
    weighted = DataArrayWeighted(da, weights)
    sum_of_weights = weighted.sum_of_weights(dim=("x", "y", "z"))
    assert sum_of_weights.values.tolist() == [[[12, 15], [18, 21]]]
    assert sum_of_weights.dims == ("x", "y", "z")

def test_weighted_sum_3d():
    da = DataArray([[[0, 1], [2, 3]], [[4, 5], [6, 7]]], dims=("x", "y", "z"))
    weights = DataArray([[[1, 2], [3, 4]], [[5, 6], [7, 8]]], dims=("x", "y", "z"))
    weighted = DataArrayWeighted(da, weights)
    sum = weighted.sum(dim=("x", "y", "z"))
    assert sum.values.tolist() == [[[3, 7], [11, 15]]]
    assert sum.dims == ("x", "y", "z")

def test_weighted_mean_3d():
    da = DataArray([[[0, 1], [2, 3]], [[4, 5], [6, 7]]], dims=("x", "y", "z"))
    weights = DataArray([[[1, 2], [3, 4]], [[5, 6], [7, 8]]], dims=("x", "y", "z"))
    weighted = DataArrayWeighted(da, weights)
    mean = weighted.mean(dim=("x", "y", "z"))
    assert mean.values.tolist() == [[[0.5, 1.5], [2.5, 3.5]]]
    assert mean.dims == ("x", "y", "z")

def test_weighted_sum_of_weights_2d_keep_attrs():
    da = DataArray([[0, 1], [2, 3]], dims=("x", "y"))
    weights = DataArray([[1, 2], [3, 4]], dims=("x", "y"))
    weighted = DataArrayWeighted(da, weights)
    sum_of_weights = weighted.sum_of_weights(dim=("x", "y"), keep_attrs=True)
    assert sum_of_weights.values.tolist() == [[3, 6]]
    assert sum_of_weights.dims == ("x", "y")
    assert sum_of_weights.attrs == {"units": "weighted"}

def test_weighted_sum_2d_keep_attrs():
    da = DataArray([[0, 1], [2, 3]], dims=("x", "y"))
    weights = DataArray([[1, 2], [3, 4]], dims=("x", "y"))
    weighted = DataArrayWeighted(da, weights)
    sum = weighted.sum(dim=("x", "y"), keep_attrs=True)
    assert sum.values.tolist() == [[1, 3]]
    assert sum.dims == ("x", "y")
    assert sum.attrs == {"units": "weighted"}

def test_weighted_mean_2d_keep_attrs():
    da = DataArray([[0, 1], [2, 3]], dims=("x", "y"))
    weights = DataArray([[1, 2], [3, 4]], dims=("x", "y"))
    weighted = DataArrayWeighted(da, weights)
    mean = weighted.mean(dim=("x", "y"), keep_attrs=True)
    assert mean.values.tolist() == [[0.5, 1.5]]
    assert mean.dims == ("x", "y")
    assert mean.attrs == {"units": "weighted"}

def test_weighted_sum_of_weights_3d_keep_attrs():
    da = DataArray([[[0, 1], [2, 3]], [[4, 5], [6, 7]]], dims=("x", "y", "z"))
    weights = DataArray([[[1, 2], [3, 4]], [[5, 6], [7, 8]]], dims=("x", "y", "z"))
    weighted = DataArrayWeighted(da, weights)
    sum_of_weights = weighted.sum_of_weights(dim=("x", "y", "z"), keep_attrs=True)
    assert sum_of_weights.values.tolist() == [[[12, 15], [18, 21]]]
    assert sum_of_weights.dims == ("x", "y", "z")
    assert sum_of_weights.attrs == {"units": "weighted"}

def test_weighted_sum_3d_keep_attrs():
    da = DataArray([[[0, 1], [2, 3]], [[4, 5], [6, 7]]], dims=("x", "y", "z"))
    weights = DataArray([[[1, 2], [3, 4]], [[5, 6], [7, 8]]], dims=("x", "y", "z"))
    weighted = DataArrayWeighted(da, weights)
    sum = weighted.sum(dim=("x", "y", "z"), keep_attrs=True)
    assert sum.values.tolist() == [[[3, 7], [11, 15]]]
    assert sum.dims == ("x", "y", "z")
    assert sum.attrs == {"units": "weighted"}

def test_weighted_mean_3d_keep_attrs():
    da = DataArray([[[0, 1], [2, 3]], [[4, 5], [6, 7]]], dims=("x", "y", "z"))
    weights = DataArray([[[1, 2], [3, 4]], [[5, 6], [7, 8]]], dims=("x", "y", "z"))
    weighted = DataArrayWeighted(da, weights)
    mean = weighted.mean(dim=("x", "y", "z"), keep_attrs=True)
    assert mean.values.tolist() == [[[0.5, 1.5], [2.5, 3.5]]]
    assert mean.dims == ("x", "y", "z")
    assert mean.attrs == {"units": "weighted"}

def test_weighted_sum_of_weights_2d_keep_attrs_false():
    da = DataArray([[0, 1], [2, 3]], dims=("x", "y"))
    weights = DataArray([[1, 2], [3, 4]], dims=("x", "y"))
    weighted = DataArrayWeighted(da, weights)
    sum_of_weights = weighted.sum_of_weights(dim=("x", "y"), keep_attrs=False)
    assert sum_of_weights.values.tolist() == [[3, 6]]
    assert sum_of_weights.dims == ("x", "y")
    assert sum_of_weights.attrs == {}

def test_weighted_sum_2d_keep_attrs_false():
    da = DataArray([[0, 1], [2, 3]], dims=("x", "y"))
    weights = DataArray([[1, 2], [3, 4]], dims=("x", "y"))
    weighted = DataArrayWeighted(da, weights)
    sum = weighted.sum(dim=("x", "y"), keep_attrs=False)
    assert sum.values.tolist() == [[1, 3]]
    assert sum.dims == ("x", "y")
    assert sum.attrs == {}

def test_weighted_mean_2d_keep_attrs_false():
    da = DataArray([[0, 1], [2, 3]], dims=("x", "y"))
    weights = DataArray([[1, 2], [3, 4]], dims=("x", "y"))
    weighted = DataArrayWeighted(da, weights)
    mean = weighted.mean(dim=("x", "y"), keep_attrs=False)
    assert mean.values.tolist() == [[0.5, 1.5]]
    assert mean.dims == ("x", "y")
    assert mean.attrs == {}

def test_weighted_sum_of_weights_3d_keep_attrs_false():
    da = DataArray([[[0, 1], [2, 3]], [[4, 5], [6, 7]]], dims=("x", "y", "z"))
    weights = DataArray([[[1, 2], [3, 4]], [[5, 6], [7, 8]]], dims=("x", "y", "z"))
    weighted = DataArrayWeighted(da, weights)
    sum_of_weights = weighted.sum_of_weights(dim=("x", "y", "z"), keep_attrs=False)
    assert sum_of_weights.values.tolist() == [[[12, 15], [18, 21]]]
    assert sum_of_weights.dims == ("x", "y", "z")
    assert sum_of_weights.attrs == {}

def test_weighted_sum_3d_keep_attrs_false():
    da = DataArray([[[0, 1], [2, 3]], [[4, 5], [6, 7]]], dims=("x", "y", "z"))
    weights = DataArray([[[1, 2], [3, 4]], [[5, 6], [7, 8]]], dims=("x", "y", "z"))
    weighted = DataArrayWeighted(da, weights)
    sum = weighted.sum(dim=("x", "y", "z"), keep_attrs=False)
    assert sum.values.tolist() == [[[3, 7], [11, 15]]]
    assert sum.dims == ("x", "y", "z")
    assert sum.attrs == {}

def test_weighted_mean_3d_keep_attrs_false():
    da = DataArray([[[0, 1], [2, 3]], [[4, 5], [6, 7]]], dims=("x", "y", "z"))
    weights = DataArray([[[1, 2], [3, 4]], [[5, 6], [7, 8]]], dims=("x", "y", "z"))
    weighted = DataArrayWeighted(da, weights)
    mean = weighted.mean(dim=("x", "y", "z"), keep_attrs=False)
    assert mean.values.tolist() == [[[0.5, 1.5], [2.5, 3.5]]]
    assert mean.dims == ("x", "y", "z")
    assert mean.attrs == {}

def test_weighted_sum_of_weights_2d_drop():
    da = DataArray([[0, 1], [2, 3]], dims=("x", "y"))
    weights = DataArray([[1, 2], [3, 4]], dims=("x", "y"))
    weighted = DataArrayWeighted(da, weights)
    sum_of_weights = weighted.sum_of_weights(dim=("x", "y"), drop=True)
    assert sum_of_weights.values.tolist() == [3, 6]
    assert sum_of_weights.dims == ("x",)

def test_weighted_sum_2d_drop():
    da = DataArray([[0, 1], [2, 3]], dims=("x", "y"))
    weights = DataArray([[1, 2], [3, 4]], dims=("x", "y"))
    weighted = DataArrayWeighted(da, weights)
    sum = weighted.sum(dim=("x", "y"), drop=True)
    assert sum.values.tolist() == [1, 3]
    assert sum.dims == ("x",)

def test_weighted_mean_2d_drop():
    da = DataArray([[0, 1], [2, 3]], dims=("x", "y"))
    weights = DataArray([[1, 2], [3, 4]], dims=("x", "y"))
    weighted = DataArrayWeighted(da, weights)
    mean = weighted.mean(dim=("x", "y"),