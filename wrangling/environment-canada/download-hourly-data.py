import pandas as pd

# Import local library
import ecweather

# Input parameters
datadir = 'data/raw/'
year = 2017
months = range(1, 13)

# Stations metadata
stations_info = pd.read_csv('data/airport_stations.csv', index_col=0)
stations = list(stations_info.index)

# Download csv files
for station, env_canada_id in stations_info['Env Canada ID'].items():
    print(f'Downloading data for {station}')
    for month in months:
        savefile = f'{datadir}weather_hourly_{station}_{year}{month:02d}.csv'
        ecweather.download_hourly_raw(env_canada_id, year, month, savefile=savefile)
print('Done!')