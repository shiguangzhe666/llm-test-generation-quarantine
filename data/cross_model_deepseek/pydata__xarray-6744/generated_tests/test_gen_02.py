import pytest
import xarray as xr

def test_DataArrayRolling_reduce():
    da = xr.DataArray([1, 2, 3, 4, 5], dims='time')
    rolling = DataArrayRolling(da, 'time', 2)
    result = rolling.reduce(lambda x: x.sum())
    expected = xr.DataArray([3, 7, 9], dims='time')
    assert result.equals(expected)

def test_DataArrayRolling_construct():
    da = xr.DataArray([1, 2, 3, 4, 5], dims='time')
    rolling = DataArrayRolling(da, 'time', 2)
    result = rolling.construct(window_dim='new_time', stride=2)
    expected = xr.DataArray([3, 7], dims='new_time')
    assert result.equals(expected)

def test_DataArrayRolling_Groupby():
    da = xr.DataArray([1, 2, 3, 4, 5], dims='time')
    grouped = DataArrayRolling(da, 'time', 2).groupby('time')
    result = grouped.reduce(lambda x: x.sum())
    expected = xr.DataArray([3, 7], dims='time')
    assert result.equals(expected)

def test_DataSetRolling_reduce():
    ds = xr.Dataset({'a': xr.DataArray([1, 2, 3, 4, 5], dims='time')})
    rolling = DataSetRolling(ds, 'time', 2)
    result = rolling.reduce(lambda x: x.sum())
    expected = xr.Dataset({'a': xr.DataArray([3, 7], dims='time')})
    assert result.equals(expected)

def test_DataSetRolling_construct():
    ds = xr.Dataset({'a': xr.DataArray([1, 2, 3, 4, 5], dims='time')})
    rolling = DataSetRolling(ds, 'time', 2)
    result = rolling.construct(window_dim='new_time', stride=2)
    expected = xr.Dataset({'a': xr.DataArray([3, 7], dims='new_time')})
    assert result.equals(expected)

def test_DataSetRolling_Groupby():
    ds = xr.Dataset({'a': xr.DataArray([1, 2, 3, 4, 5], dims='time')})
    grouped = DataSetRolling(ds, 'time', 2).groupby('time')
    result = grouped.reduce(lambda x: x.sum())
    expected = xr.Dataset({'a': xr.DataArray([3, 7], dims='time')})
    assert result