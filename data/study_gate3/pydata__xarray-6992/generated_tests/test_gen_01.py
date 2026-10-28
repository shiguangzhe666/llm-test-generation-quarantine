import xarray as xr
import numpy as np
import pandas as pd

# Define coordinates
lon = [-99.83, -99.32, -99.79, -99.23]
lat = [42.25, 42.21, 42.63, 42.59]
time = pd.to_datetime(['2014-09-06', '2014-09-07', '2014-09-08'])
reference_time = pd.to_datetime('2014-09-05')

# Create temperature and precipitation arrays
# Assuming the minimum temperature is at (x=1, y=1, time=2)
temperature = np.full((4, 4, 3), np.nan)
temperature[1, 1, 2] = 7.182  # minimum temperature value
precipitation = np.full((4, 4, 3), np.nan)
precipitation[1, 1, 2] = 8.326  # corresponding precipitation value

# Create the dataset
ds = xr.Dataset(
    {
        'temperature': (['x', 'y', 'time'], temperature),
        'precipitation': (['x', 'y', 'time'], precipitation),
    },
    coords={
        'x': lon,
        'y': lat,
        'time': time,
        'reference_time': reference_time,
    }
)

# Find the indices of the minimum temperature
min_temp_idx = ds.temperature.argmin(dim=['x', 'y', 'time'])

# Use isel to select the point
min_temp_point = ds.isel(x=min_temp_idx.x, y=min_temp_idx.y, time=min_temp_idx.time)

# Output the values
print("Minimum Temperature:", min_temp_point.temperature.values)
print("Precipitation at that point:", min_temp_point.precipitation.values)

# Minimum Temperature: [7.182]
# Precipitation at that point: [8.326]
