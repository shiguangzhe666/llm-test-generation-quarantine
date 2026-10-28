import xarray as xr

def test_coarsen():
    # create a sample dataset
    data = [[1, 2, 3, 4, 5], [6, 7, 8, 9, 10], [11, 12, 13, 14, 15]]
    dims = ['x', 'y']
    coords = {'x': [0, 1, 2], 'y': [0, 1, 2]}
    ds = xr.Dataset({'data': (dims, data)}, coords=coords)

    # test coarsen()
    actual = ds.coarsen(x=2, y=3, boundary=False).mean()
    expected = xr.Dataset({'data': [[4.5, 6], [10.5, 12]]}, coords=coords)
    assert actual.equals(expected)

    # test coarsen() with boundary=True
    actual = ds.coarsen(x=2, y=3, boundary=True).mean()
    expected = xr.Dataset({'data': [[4.5, 6], [10.5, 12], [18.5, 20]]}, coords=coords)
    assert actual.equals(expected)

    # test coarsen() with a list of dimensions
    actual = ds.coarsen([x=2, y=3], boundary=False).mean()
    expected = xr.Dataset({'data': [[4.5, 6], [10.5, 12]]}, coords=coords)
    assert actual.equals(expected)

    # test coarsen() with a dictionary of dimensions
    actual = ds.coarsen({'x': 2, 'y': 3}, boundary=False).mean()
    expected = xr.Dataset({'data': [[4.5, 6], [10.5, 12]]}, coords=coords)
    assert actual.equals(expected)

    # test coarsen() with a dictionary of dimensions and a dictionary of boundary options
    actual = ds.coarsen({'x': 2, 'y': 3}, boundary={'x': False, 'y': True}).mean()
    expected = xr.Dataset({'data': [[4.5, 6], [10.5, 12], [18.5, 20]]}, coords=coords)
    assert actual.equals(expected)

if __name__ == '__main__':
    test_coarsen()