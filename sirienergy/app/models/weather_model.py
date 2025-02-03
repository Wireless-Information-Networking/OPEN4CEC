import openmeteo_requests
import requests_cache
import pandas as pd
from retry_requests import retry
import requests
from datetime import datetime
from app.config import Config

def get_weather(latitude, longitude, timezone):
    """
    Retrieves hourly weather data for a given location using the Open-Meteo API.
    
    Input:
        latitude (float): The latitude of the location.
        longitude (float): The longitude of the location.
        timezone (str): The timezone of the location (e.g., 'Europe/Berlin').
    
    Output:
        pd.DataFrame: A DataFrame containing hourly weather codes for the next 24 hours.
    """
    cache_session = requests_cache.CachedSession('.cache', expire_after=3600)
    retry_session = retry(cache_session, retries=5, backoff_factor=0.2)
    openmeteo = openmeteo_requests.Client(session=retry_session)
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
    hourly_data = {
        "date": pd.date_range(
            start=pd.to_datetime(hourly.Time(), unit="s", utc=True),
            end=pd.to_datetime(hourly.TimeEnd(), unit="s", utc=True),
            freq=pd.Timedelta(seconds=hourly.Interval()),
            inclusive="left"
        )
    }
    hourly_data["date"] = hourly_data["date"] + pd.to_timedelta(response.UtcOffsetSeconds(), unit='s')
    hourly_data["weather_code"] = hourly_weather_code
    hourly_dataframe = pd.DataFrame(data=hourly_data).head(24)
    hourly_dataframe['weather_code'] = hourly_dataframe['weather_code'].astype(int).astype(str)
    return hourly_dataframe

def get_sunrise_sunset(latitude, longitude):
    """
    Retrieves the sunrise and sunset times for a given location using the WeatherAPI.
    
    Input:
        latitude (float): The latitude of the location.
        longitude (float): The longitude of the location.
    
    Output:
        tuple: A tuple containing the sunrise and sunset times as strings (e.g., '06:30 AM', '06:00 PM').
    """
    url = f"http://api.weatherapi.com/v1/astronomy.json?key={Config.WEATHER_API_API_KEY}&q={latitude},{longitude}&aqi=no"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        return data['astronomy']['astro']['sunrise'], data['astronomy']['astro']['sunset']
    else:
        raise Exception(f"Failed to retrieve weather data. Status code: {response.status_code}")

def image_array(codes, sunrise, sunset):
    """
    Generates an array of image names based on weather codes and day/night conditions.
    
    Input:
        codes (pd.DataFrame): A DataFrame containing weather codes and timestamps.
        sunrise (str): The sunrise time in the format 'HH:MM AM/PM'.
        sunset (str): The sunset time in the format 'HH:MM AM/PM'.
    
    Output:
        list: A list of image names indicating day/night and weather conditions (e.g., 'day-100', 'night-200').
    """
    if codes is None or sunrise is None or sunset is None:
        raise ValueError("Invalid data for image generation.")

    codes['date'] = pd.to_datetime(codes['date'])
    sunrise_time = datetime.strptime(sunrise, '%I:%M %p').time()
    sunset_time = datetime.strptime(sunset, '%I:%M %p').time()

    def day_or_night(timestamp):
        time = timestamp.time()
        return 'day' if sunrise_time <= time <= sunset_time else 'night'

    codes['day_night'] = codes['date'].apply(day_or_night)
    images = codes.apply(lambda row: f"{row['day_night']}-{row['weather_code']}", axis=1)
    return images.tolist()