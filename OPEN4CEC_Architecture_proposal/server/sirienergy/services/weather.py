import logging
import openmeteo_requests
import requests_cache
import pandas as pd
from retry_requests import retry
import requests
from datetime import datetime

def get_weather(latitude, longitude, timezone):
    """
    Fetch weather data from the Open-Meteo API for a given location and return hourly weather codes.

    This function uses the Open-Meteo API to retrieve weather forecast data for a specific
    latitude and longitude, processed on an hourly basis. It requests hourly weather codes
    and converts them into a Pandas DataFrame for easy manipulation. The function also
    caches API responses and retries failed requests to ensure reliability.

    Parameters
    -----------

    latitude : float
        The latitude of the location for which weather data is requested.
    longitude : float
        The longitude of the location for which weather data is requested.
    timezone : str
        The timezone to adjust the timestamps in the returned data.

    Returns
    --------

    pandas.DataFrame
        A DataFrame containing the hourly weather data with the following columns:
        - 'date': The date and time of the weather data for each hour, adjusted to the given timezone.
        - 'weather_code': The weather condition code for each hour (as an integer converted to a string).

    Notes
    ------

    - The API responses are cached for 1 hour to limit the number of API calls.
    - In case of request failures, the function will retry up to 5 times with a backoff strategy.
    """

    cache_session = requests_cache.CachedSession('.cache', expire_after = 3600)
    retry_session = retry(cache_session, retries = 5, backoff_factor = 0.2)
    openmeteo = openmeteo_requests.Client(session = retry_session)
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "hourly": "weather_code",
        "timezone": timezone
    }
    responses = openmeteo.weather_api(url, params=params)
    response = responses[0]
    hourly = response.Hourly()
    hourly_weather_code = hourly.Variables(0).ValuesAsNumpy()
    hourly_data = {"date": pd.date_range(
        start = pd.to_datetime(hourly.Time(), unit = "s", utc = True),
        end = pd.to_datetime(hourly.TimeEnd(), unit = "s", utc = True),
        freq = pd.Timedelta(seconds = hourly.Interval()),
        inclusive = "left"
    )}
    hourly_data["date"] = hourly_data["date"] + pd.to_timedelta(response.UtcOffsetSeconds(), unit='s')
    hourly_data["weather_code"] = hourly_weather_code
    hourly_dataframe = pd.DataFrame(data = hourly_data)
    hourly_dataframe = hourly_dataframe.head(24)
    hourly_dataframe['weather_code'] = hourly_dataframe['weather_code'].astype(int).astype(str)
    return hourly_dataframe

def get_sunrise_sunset(api_key, latitude, longitude):
    """
    Fetch the sunrise and sunset times for a given location using the WeatherAPI.

    This function uses the WeatherAPI to retrieve astronomical data (sunrise and sunset)
    for a specific location identified by its latitude and longitude. The API key is
    required to authenticate the request.

    Parameters
    -----------

    api_key : str
        Your WeatherAPI key to authenticate the API request.
    latitude : float
        The latitude of the location for which sunrise and sunset times are requested.
    longitude : float
        The longitude of the location for which sunrise and sunset times are requested.

    Returns
    --------

    tuple
        A tuple containing two strings:
        - 'sunrise': The time of sunrise at the specified location (in local time).
        - 'sunset': The time of sunset at the specified location (in local time).

    If the API request fails, a dictionary is returned instead with an error message.

    Examples
    ---------

    >>> get_sunrise_sunset("your_api_key", 51.5074, -0.1278)
    ('07:15 AM', '06:45 PM')

    Notes
    -----

    - The API key must be valid for the function to work.
    - The times are returned in the local timezone of the requested location.
    """
    
    url = f"http://api.weatherapi.com/v1/astronomy.json?key={api_key}&q={latitude},{longitude}&aqi=no"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        sunrise = data['astronomy']['astro']['sunrise']
        sunset = data['astronomy']['astro']['sunset']
        
        return sunrise, sunset
    else:
        return {"error": f"Failed to retrieve weather data. Status code: {response.status_code}"}

def image_array(codes, sunrise, sunset):
    """
    Generate an array of image labels based on weather codes and the time of day (day/night).

    This function processes weather data, determines whether each weather observation
    occurs during the day or night based on the provided sunrise and sunset times, 
    and assigns an image label in the format `day/night-weather_code`.

    Parameters
    ----------

    codes : pandas.DataFrame
        A DataFrame containing weather data with at least two columns:
        - 'date': Timestamps of the weather data.
        - 'weather_code': The weather condition code.
    sunrise : str
        The local sunrise time as a string in the format '%I:%M %p' (e.g., '06:30 AM').
    sunset : str
        The local sunset time as a string in the format '%I:%M %p' (e.g., '06:30 PM').

    Returns
    -------

    list
        A list of strings where each string is a label representing the time of day ('day' or 'night') 
        and the weather condition, in the format 'day/night-weather_code'.
    
    None
        Returns None if any of the inputs (`codes`, `sunrise`, or `sunset`) is None.

    Examples
    --------

    >>> codes = pd.DataFrame({
    >>>     'date': ['2024-10-01 07:00:00', '2024-10-01 20:00:00'],
    >>>     'weather_code': ['0', '2']
    >>> })
    >>> image_array(codes, '06:30 AM', '06:30 PM')
    ['day-0', 'night-2']

    Notes:
    ------
    - The 'date' column in the `codes` DataFrame should be in a format that can be converted
      to a Pandas `datetime` object.
    - The function compares the time part of each timestamp with the sunrise and sunset times
      to determine whether it's day or night.
    """

    if codes is None or sunrise is None or sunset is None:
        return None

    codes['date'] = pd.to_datetime(codes['date'])
    sunrise_time = datetime.strptime(sunrise, '%I:%M %p').time()
    sunset_time = datetime.strptime(sunset, '%I:%M %p').time()

    def day_or_night(timestamp):
        time = timestamp.time()  # Extract only the time part
        if sunrise_time <= time <= sunset_time:
            return 'day'
        else:
            return 'night'

    codes['day_night'] = codes['date'].apply(day_or_night)
    images = codes.apply(lambda row: f"{row['day_night']}-{row['weather_code']}", axis=1)
    images_list = images.tolist()

    return images_list

