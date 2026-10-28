import xarray as xr
import numpy as np

def test_dataarray_rolling():
    da = xr.DataArray(np.arange(10), dims='x')
    result = da.rolling(x=3).mean()
    assert result.shape == (7,)
    np.testing.assert_array_equal(result.values, [np.nan, np.nan, 1., 2., 3., 4., 5.])

def test_dataset_rolling():
    da = xr.DataArray(np.arange(10), dims='x')
    ds = xr.Dataset({'a': da, 'b': da})
    result = ds.rolling(x=3).mean()
    for var in ['a', 'b']:
        np.testing.assert_array_equal(result[var].values, [np.nan, np.nan, 1., 2., 3., 4., 5.])

def test_coarsen():
    da = xr.DataArray(np.arange(10), dims='x')
    result = da.coarsen(x=2, boundary='trim').mean()
    np.testing.assert_array_equal(result.values, [0.5, 2.5, 4.5, 6.5, 8.5])

def test_rolling_min_periods():
    da = xr.DataArray(np.arange(10), dims='x')
    result = da.rolling(x=3, min_periods=2).mean()
    np.testing.assert_array_equal(result.values, [np.nan, np.nan, 1., 2., 3., 4., 5.])

def test_rolling_center():
    da = xr.DataArray(np.arange(10), dims='x')
    result = da.rolling(x=3, center=True).mean()
    np.testing.assert_array_equal(result.values, [np.nan, 0.5, 1.5, 2.5, 3.5, 4.5, np.nan])

def test_attributes():
    da = xr.DataArray(np.arange(10), dims='x', attrs={'test': 1})
    result = da.rolling(x=3).mean(keep_attrs=True)
    assert 'test' in result.attrs
    result = da.rolling(x=3).mean(keep_attrs=False)
    assert 'test' not in result.attrs