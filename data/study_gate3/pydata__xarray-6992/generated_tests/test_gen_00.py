import xarray as xr
import numpy as np
import pandas as pd

# Define coordinates
lon = [-99.83, -99.32, -99.79, -99.23]
lat = [42.25, 42.21, 42.63, 42.59]
time = pd.to_datetime(['2014-09-06', '2014-09-07', '2014-09-08'])

# Create temperature data with the minimum at (x=1, y=1, time=2)
temperature_data = np.array([
    [[29.11, 18.2, 22.83],
     [18.28, 16.15, 26.63],
     [17.3, 15.4, 20.1],
     [19.0, 14.5, 21.2]],
    [[20.0, 16.0, 22.5],
     [17.0, 14.0, 23.0],
     [18.5, 12.5, 24.0],
     [19.5, 13.0, 25.0]],
    [[21.0, 17.0, 23.0],
     [18.0, 13.0, 24.0],
     [19.5, 11.5, 25.5],
     [20.0, 12.0, 26.0]],
    [[22.0, 18.0, 24.0],
     [19.0, 14.0, 25.0],
     [20.5, 10.0, 26.5],
     [21.0, 11.0, 27.0]],
])

# Create precipitation data
precipitation_data = np.array([
    [[0.5, 1.2, 3.0],
     [1.0, 2.5, 4.0],
     [1.5, 3.0, 5.0],
     [2.0, 3.5, 6.0]],
    [[0.7, 1.5, 3.5],
     [1.2, 2.8, 5.0],
     [1.8, 3.2, 6.0],
     [2.3, 3.8, 7.0]],
    [[0.9, 1.7, 4.0],
     [1.4, 3.0, 6.0],
     [2.0, 3.5, 7.0],
     [2.5, 4.0, 8.0]],
    [[1.1, 1.9, 4.5],
     [1.6, 3.2, 7.0],
     [2.2, 3.7, 8.0],
     [2.7, 4.2, 9.0]],
])

# Construct the Dataset
ds = xr.Dataset(
    {
        'temperature': (['x', 'y', 'time'], temperature_data),
        'precipitation': (['x', 'y', 'time'], precipitation_data),
    },
    coords={
        'x': np.arange(len(lon)),
        'y': np.arange(len(lat)),
        'lon': ('x', lon),
        'lat': ('y', lat),
        'time': time,
    }
)

# Find the index of the minimum temperature
min_idx = ds.temperature.argmin()

# Select the minimum temperature location
min_ds = ds.isel(x=min_idx.x, y=min_idx.y, time=min_idx.time)

# Verify the result
assert np.isclose(min_ds.temperature.values, 10.0), "Minimum temperature not found"
assert np.isclose(min_ds.precipitation.values, 3.0), "Precipitation value mismatch"
assert np.array_equal(min_ds.time.values, time[2]), "Incorrect time selected"
assert np.array_equal(min_ds.lon.values, lon[1]), "Incorrect longitude selected"
assert np.array_equal(min_ds.lat.values, lat[1]), "Incorrect latitude selected"

print("Test passed!")