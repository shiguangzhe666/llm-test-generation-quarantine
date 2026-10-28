import xarray as xr
import numpy as np

# Test DataArray coarsen
da = xr.DataArray(np.random.rand(4, 4), dims=('x', 'y'))
coarsened_da = da.coarsen(x=2, y=2)
assert isinstance(coarsened_da, xr.DataArray), "Coarsened object should be a DataArray"
assert coarsened_da.x.size == 2, "Coarsened x dimension should be halved"
assert coarsened_da.y.size == 2, "Coarsened y dimension should be halved"

# Test Dataset coarsen
ds = xr.Dataset({'a': da, 'b': da * 2})
coarsened_ds = ds.coarsen(x=2, y=2)
assert isinstance(coarsened_ds, xr.Dataset), "Coarsened object should be a Dataset"
assert 'a' in coarsened_ds.data_vars, "Coarsened dataset should have the same variables as the original"
assert 'b' in coarsened_ds.data_vars, "Coarsened dataset should have the same variables as the original"
assert coarsened_ds['a'].x.size == 2, "Coarsened x dimension should be halved"
assert coarsened_ds['b'].y.size == 2, "Coarsened y dimension should be halved"

# Test CoarsenArithmetic
coarsened_da_arith = coarsened_da.mean(dim='x', keep_attrs=True)
assert isinstance(coarsened_da_arith, xr.DataArray), "Coarsened arithmetic result should be a DataArray"
assert 'x' not in coarsened_da_arith.dims, "x dimension should not be in the result"
assert 'y' in coarsened_da_arith.dims, "y dimension should be in the result"

# Test Coarsen with boundary
da = xr.DataArray(np.random.rand(5, 5), dims=('x', 'y'))
coarsened_da_bound = da.coarsen(x=2, y=2, boundary='trim')
assert coarsened_da_bound.x.size == 2, "Coarsened x dimension should be halved with trim boundary"
assert coarsened_da_bound.y.size == 2, "Coarsened y dimension should be halved with trim boundary"