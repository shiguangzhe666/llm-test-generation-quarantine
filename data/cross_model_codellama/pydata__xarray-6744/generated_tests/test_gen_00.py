import xarray as xr

def test_coarsen():
    # create sample data
    dim1 = ["A", "B", "C"]
    dim2 = ["X", "Y", "Z"]
    data = np.random.rand(3, 3, 3)
    coords = {"dim1": dim1, "dim2": dim2}
    da = xr.DataArray(data, coords=coords, dims=["dim1", "dim2"])

    # test coarsen
    assert np.array_equal(da.coarsen(dim1, 2).values, data[:2, :, :])
    assert np.array_equal(da.coarsen(dim2, 2).values, data[:, :2, :])
    assert np.array_equal(da.coarsen(dim1, 2, boundary=True).values, data[:3, :, :])
    assert np.array_equal(da.coarsen(dim2, 2, boundary=True).values, data[:, :3, :])
    assert np.array_equal(da.coarsen(dim1, 2, boundary=True, fill_value=0).values, data[:3, :, :])
    assert np.array_equal(da.coarsen(dim2, 2, boundary=True, fill_value=0).values, data[:, :3, :])