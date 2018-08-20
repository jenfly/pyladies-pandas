import numpy as np
import pandas as pd
import requests

def download_hourly_raw(env_canada_id, year, month, savefile='test.csv', verbose=True):
    """Download csv file of hourly data for selected station, year, and month"""
    
    # URL endpoint and query parameters
    url_endpoint = 'http://climate.weather.gc.ca/climate_data/bulk_data_e.html'
    params = {'format' : 'csv', 
              'stationID' : env_canada_id,
              'Year' : year,
              'Month' : f'{month:02d}',
              'Day' : '01',
              'timeframe' : '1',
              'submit' : ' Download Data'}

    # Send GET request
    response = requests.get(url_endpoint, params=params)
    
    # Download csv file
    if verbose:
        print(f'Saving to {savefile}')
    with open(savefile, 'wb') as f:
        f.write(response.content)
    
    return None


def read_hourly_raw(csv_file, pre_process=True, skiprows=15):
    """Read hourly weather data from CSV file, and return as a DataFrame.
    
    If argument `pre_process` is True, some minor pre-processing is applied
    to the DataFrame: adjust some column labels, and include only the columns
    we're interested in.
    """
    df = pd.read_csv(csv_file, skiprows=skiprows, index_col=0, parse_dates=True)
    
    if pre_process:
        # Remove redundant time columns and any columns with label ending in "Flag"
        time_cols = ['Year', 'Month', 'Day' , 'Time']
        flag_cols = [col for col in df.columns if col.endswith('Flag')]        
        df = df.drop(time_cols + flag_cols, axis=1)
        
        # Remove non-ascii degree symbol from column labels
        # and rename 'Weather' to 'Conditions'
        def adjust_label(label):
            return label.replace('\xb0', 'deg ').replace('Weather', 'Conditions')
        columns = [adjust_label(col) for col in df.columns]
        df.columns = columns
        
        # Rename datetime index
        df.index.name = 'Datetime (Local Standard)'
    
    return df


def load_hourly_data(csv_files, pre_process=True, skiprows=15, verbose=True):
    """Read raw hourly data from list of csv files, merge, and return as a DataFrame
    
    If argument `pre_process` is True, some minor pre-processing is applied
    to the DataFrame: adjust some column labels, and include only the columns
    we're interested in.
    """
    df_list = []
    for csv_file in csv_files:
        if verbose:
            print(f'Reading {csv_file}')
        df_in = read_hourly_raw(csv_file, pre_process=pre_process, skiprows=skiprows)
        df_list.append(df_in)
    data = pd.concat(df_list, axis=0)
    return data


def process_hourly_data(data, station, stations_info, verbose=True):
    """Process hourly weather data and station metadata, and return as a DataFrame"""
    
    # Check for any rows where all measurements are missing
    all_missing = data.isnull().all(axis=1)
    if verbose:
        print(f'{all_missing.value_counts().get(True)} rows with all measurements missing')

    # Assume weather category persists until indicated otherwise by a new non-null value
    # so use forward filling, except if all other measurements are missing, then leave as null
    data_out = data.copy()
    data_out['Conditions'] = data_out['Conditions'].fillna(method='ffill')
    data_out.loc[all_missing, 'Conditions'] = np.nan
    
    # Convert wind direction from 10s of degrees to degrees
    data_out['Wind Dir (deg)'] = 10 * data_out['Wind Dir (10s deg)']

    # Add station metadata
    data_out['Station ID'] = station
    data_out['Station Name'] = stations_info.loc[station, 'Name']
    data_out['Timezone'] = stations_info.loc[station, 'Timezone']

    # Calculate UTC datetimes
    utc_offset_hours =  stations_info.loc[station, 'UTC Offset (hours)']
    tdelta = pd.Timedelta(-utc_offset_hours, unit='h')
    data_out['Datetime (UTC)'] = data_out.index + tdelta
    
    # Reorder columns
    columns = ['Station ID', 'Station Name', 'Timezone', 'Datetime (UTC)', 
               'Temp (deg C)', 'Dew Point Temp (deg C)', 'Rel Hum (%)', 
               'Wind Dir (deg)', 'Wind Spd (km/h)', 'Visibility (km)', 
               'Stn Press (kPa)', 'Hmdx', 'Wind Chill', 'Conditions']
    data_out = data_out[columns]
    
    return data_out
