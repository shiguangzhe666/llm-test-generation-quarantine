import xarray as xr
import numpy as np

# Test Data
data = np.random.rand(4, 4)
dim = ['x', 'y']
coords = {'x': [10, 20, 30, 40], 'y': [1, 2, 3, 4]}
ds = xr.Dataset({'a': ('x', 'y', data)}, coords=coords)

# Testing Coarsen
def test_coarsen():
    coarsened = ds.coarsen(x=2, y=2)
    result = coarsened.sum()
    expected = ds.assign(a=lambda ds: ds.a.coarsen(x=2, y=2).sum()).isel(x=slice(None, None, 2), y=slice(None, None, 2))
    assert np.allclose(result['a'], expected['a'])

def test_rolling():
    rolled = ds.rolling(x=2, y=2)
    result = rolled.mean()
    expected = ds.assign(a=lambda ds: ds.a.rolling(x=2, y=2).mean())
    assert np.allclose(result['a'], expected['a'])

test_coarsen()
test_rolling()