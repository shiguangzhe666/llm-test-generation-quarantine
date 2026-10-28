import xarray as xr
import numpy as np
import pytest

def test_rolling_mean():
    data = np.random.rand(10, 3)
    da = xr.DataArray(data, dims=['time', 'x'])
    rolled = da.rolling(time=3, min_periods=1).mean()
    assert rolled.shape == (10, 3)
    assert np.isnan(rolled[0, :].values).all()
    assert np.isnan(rolled[1, :].values).all()
    assert np.isnan(rolled[2, :].values).all()
    assert not np.isnan(rolled[3, :].values).any()

def test_dataset_rolling():
    data = np.random.rand(10, 3)
    ds = xr.Dataset({'temp': ('time', data)}, coords={'time': np.arange(10)})
    rolled = ds.rolling(time=3, min_periods=1).mean()
    assert rolled['temp'].shape == (10, 3)
    assert np.isnan(rolled['temp'][0, :].values).all()
    assert np.isnan(rolled['temp'][1, :].values).all()
    assert np.isnan(rolled['temp'][2, :].values).all()
    assert not np.isnan(rolled['temp'][3, :].values).any()

def test_rolling_with_fillna():
    data = np.random.rand(10, 3)
    da = xr.DataArray(data, dims=['time', 'x'])
    rolled = da.rolling(time=3, min_periods=1).mean(fillna=True)
    assert rolled.shape == (10, 3)
    assert not np.isnan(rolled[0, :].values).any()
    assert not np.isnan(rolled[1, :].values).any()
    assert not np.isnan(rolled[2, :].values).any()
    assert not np.isnan(rolled[3, :].values).any()