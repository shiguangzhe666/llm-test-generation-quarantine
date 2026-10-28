import xarray as xr
import numpy as np
import pytest

def test_dataarray_rolling_mean():
    data = np.arange(10)
    da = xr.DataArray(data, dims='x')
    rolled = da.rolling(window=3, min_periods=2)
    result = rolled.mean()
    assert result.shape == (8,)
    np.testing.assert_array_equal(result.values, [0.5, 1.5, 2.5, 3.5, 4.5, 5.5, 6.5, 7.5])

def test_dataset_rolling_mean():
    data = np.arange(10)
    ds = xr.Dataset({
        'a': ('x', data),
        'b': ('x', data)
    }, coords={'x': np.arange(10)})
    rolled = ds.rolling(window=3, min_periods=2)
    result = rolled.mean()
    assert all(result['a'].shape == (8,) and result['b'].shape == (8,))

def test_dataarray_rolling_construct():
    data = np.arange(10)
    da = xr.DataArray(data, dims='x')
    rolled = da.rolling(window=3)
    result = rolled.construct(window_dim='window')
    assert 'window' in result.dims
    assert result.shape == (8, 3)

def test_dataset_rolling_construct():
    data = np.arange(10)
    ds = xr.Dataset({
        'a': ('x', data),
    }, coords={'x': np.arange(10)})
    rolled = ds.rolling(window=3)
    result = rolled.construct(window_dim='window')
    assert 'window' in result.dims
    assert result['a'].shape == (8, 3)