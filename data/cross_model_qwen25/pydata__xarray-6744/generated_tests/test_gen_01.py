import xarray as xr
import numpy as np

# Define test data
data = np.random.rand(4, 4)
coords = {'x': ['A', 'B', 'C', 'D'], 'y': ['1', '2', '3', '4']}
dims = ('x', 'y')
ds = xr.Dataset({'a': (dims, data), 'b': (dims, 2 * data)}, coords=coords)

# Define test rolling and coarsen objects
dim = 'x'
window = 2
center = False
windows = {'x': window}
boundary = 'trim_excess'

# Test Rolling
rolling = ds.rolling(dim=dim, window=window, center=center)
result_rolling = rolling.reduce(func=np.sum, skipna=True)
assert result_rolling['a'].values.shape == (2, 4)

# Test Coarsen
coarsen = rolling.coarsen(dim=dim, other=[{'x': 2}])
result_coarsen = coarsen.reduce(func=np.sum, skipna=True)
assert result_coarsen['a'].values.shape == (2, 4)

# Test boundary parameter
rolling = ds.rolling(dim=dim, window=window, boundary=boundary)
result_rolling_boundary = rolling.reduce(func=np.sum, skipna=True)
assert result_rolling_boundary['a'].values.shape == (2, 4)