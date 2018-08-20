import pandas as pd

# Import local library
import ecweather

# Specify data directories and date ranges to process
datadir = 'data/raw/'
savedir = 'data/processed/'
year = 2017
months = range(1, 13)
months_str = f'{year}{min(months):02d}-{year}{max(months):02d}'

# Stations metadata
stations_info = pd.read_csv('data/airport_stations.csv', index_col=0)
stations = list(stations_info.index)

# Process hourly data for each station and save to csv files
for station in stations:
    csv_files = [f'{datadir}weather_hourly_{station}_{year}{month:02d}.csv' for month in months]
    savefile = f'{savedir}weather_hourly_{station}_{months_str}.csv'
    data_in = ecweather.load_hourly_data(csv_files)
    data_out = ecweather.process_hourly_data(data_in, station, stations_info)
    print(f'Saving to {savefile}')
    data_out.to_csv(savefile)
print('Done!')