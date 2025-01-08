import logging
import requests
from datetime import datetime, timedelta
import xmltodict
from services.entsoe_aux import load_entsoe_country_keys
import json

def get_day_ahead_prices(ENTSO_E_API_KEY, country_name):
    # Get the endpoint
    endpoint = 'https://web-api.tp.entsoe.eu/api'

    # Get query parameters
        #Time (Always today)
    current_datetime = datetime.now()
    yesterday_datetime = current_datetime - timedelta(days=1)
    current_formatted = current_datetime.strftime('%Y%m%d') + '2200'
    yesterday_formatted = yesterday_datetime.strftime('%Y%m%d') + '2200'
        #Country key (According to the country)
    entsoe_country_keys = load_entsoe_country_keys()
    if country_name not in entsoe_country_keys:
        logging.error(f"Key for country {country_name} not found")
        return
    country_key=entsoe_country_keys[country_name]

    params = {
        'securityToken': ENTSO_E_API_KEY,
        'documentType': 'A44',  # Day-ahead Prices
        'in_Domain': country_key,  # Place (entsoe_key.csv)
        'out_Domain': country_key,
        'periodStart': yesterday_formatted,  # Start time (yyyymmddhhmm)
        'periodEnd': current_formatted       # End time (yyyymmddhhmm)
    }
    
    # Make the query
    response = requests.get(endpoint, params=params)

    # Transform the query response to JSON dictionary
    data_xml = response.text
    data_dict = xmltodict.parse(data_xml)
    data_json = json.loads(json.dumps(data_dict))

    # Handle the response
    if response.status_code == 200:

        time_series_list = data_json['Publication_MarketDocument'].get('TimeSeries', [])

        # Case 1: Data is in different formats, and we need to get only PT60
        if isinstance(time_series_list, list) and len(time_series_list) > 0:
            for time_series in time_series_list:
                if time_series['Period']['resolution'] == 'PT60M':
                    points = time_series['Period']['Point']
                    break  
            else:
                points = []
        # Case 2: Data is only in the format we want
        elif time_series_list['Period']['resolution'] == 'PT60M':
            points = time_series_list['Period']['Point']
        # Case 3: Any other format
        else:
            logging.info(f"Case 3: Incorrect format: {time_series_list}")
            points = []
        
        return points
    else:
        logging.error(f"Failed to retrieve data. Status code: {response.status_code}")
        logging.error(f"Error response: {data_json}")
        return {"error": f"Failed to retrieve data. Status code: {response.status_code}"}