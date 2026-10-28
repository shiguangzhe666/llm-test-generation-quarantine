import pytest
import xarray as xr

def test_coarsen():
    ds = xr.Dataset(
        {
            "data": (["time", "lat", "lon"], [1] * 100),
        },
        coords={
            "time": pd.date_range(start='01-01-2000', periods=100),
            "lat": [1] * 100,
            "lon": [1] * 100,
        }
    )
    result = ds.coarsen(time=10).mean()
    assert result["data"].dims == ("lat", "lon")