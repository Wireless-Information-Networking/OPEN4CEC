import pvlib
import pandas as pd
from datetime import datetime

def get_PV_gen(latitude, longitude, altitude, surface, efficiency, tz):
    """
    Calculates the photovoltaic (PV) power generation for a given location and system configuration.
    
    Input:
        latitude (float): The latitude of the location.
        longitude (float): The longitude of the location.
        altitude (float): The altitude of the location in meters.
        surface (float): The surface area of the PV panels in square meters.
        efficiency (float): The efficiency of the PV panels as a percentage.
        tz (str): The timezone of the location (e.g., 'Europe/Berlin').
    
    Output:
        list: A list of hourly PV power generation values in watts.
    """
    # Create a location object using pvlib
    location = pvlib.location.Location(latitude, longitude, tz=tz, altitude=altitude)

    # Define a time range: single day, with an hourly frequency
    times = pd.date_range(start=datetime(2024, 9, 21, 0), end=datetime(2024, 9, 21, 23, 59), freq='1h', tz=tz)

    # Calculate the clear sky solar radiation using the Ineichen clear sky model
    clearsky = location.get_clearsky(times, model='ineichen')  # DataFrame with GHI, DNI, DHI

    # Access the Global Horizontal Irradiance (GHI)
    ghi = clearsky['ghi']

    # Convert GHI to a list (array)
    ghi_array = ghi.tolist()

    # Log the entire clearsky DataFrame
    #logging.info(ghi_array)
    #logging.info(f'Efficiency: {efficiency}')
    #logging.info(f'Surface: {surface}')

    const = efficiency/100
    const = const * surface

    #logging.info(f'Const: {const}')

    power_array = [x * const for x in ghi_array]
    #logging.info(power_array)

    return power_array