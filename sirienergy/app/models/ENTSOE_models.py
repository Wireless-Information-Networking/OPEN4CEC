import csv
import logging
import requests
from datetime import datetime, timedelta
import xmltodict
import json
from app.config import Config
import os

def load_entsoe_country_keys():
    """
    Loads country keys from a CSV file for ENTSO-E API queries.
    
    Input: 
        None

    Output: 
        dict: A dictionary mapping country names to their respective ENTSO-E keys.
    """
    # Dynamically construct the path to the CSV file
    base_dir = os.path.dirname(__file__)  # Directory of the current module
    file_path = os.path.join(base_dir, '../aux/entsoe_tables/entsoe_country_keys.csv')
    file_path = os.path.abspath(file_path)  # Resolve to an absolute path

    entsoe_country_keys = {}
    with open(file_path, mode='r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            entsoe_country_keys[row['country']] = row['key']
    return entsoe_country_keys

def load_entsoe_gentype_names():
    """
    Loads generation type names from a CSV file for ENTSO-E API queries.
    
    Input: 
        None

    Output: 
        dict: A dictionary mapping ENTSO-E generation type keys to their respective names.
    """
    # Dynamically construct the path to the CSV file
    base_dir = os.path.dirname(__file__)  # Directory of the current module
    file_path = os.path.join(base_dir, '../aux/entsoe_tables/entsoe_gentype_names.csv')
    file_path = os.path.abspath(file_path)  # Resolve to an absolute path

    entsoe_gentype_names = {}
    with open(file_path, mode='r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            entsoe_gentype_names[row['key']] = row['name']
    return entsoe_gentype_names

def get_day_ahead_prices(country_name):
    """
    Retrieves day-ahead electricity prices for a specified country using the ENTSO-E API.
    
    Input:
        country_name (str): The name of the country for which to retrieve prices.
    
    Output:
        list: A list of price points for the day-ahead market, or an error message if the request fails.
    """
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
        'securityToken': Config.ENTSO_E_API_KEY,
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

def load_co2_by_type(file_path='entsoe_tables/CO2.csv'):
    """
    Loads CO2 emission factors by generation type from a CSV file.
    
    Input:
        file_path (str, optional): The path to the CSV file. Defaults to 'entsoe_tables/CO2.csv'.
    
    Output:
        dict: A dictionary mapping energy types to their respective CO2 emission factors (gCO2eq/Wh).
    """
    base_dir = os.path.dirname(__file__)  # Directory of the current module
    file_path = os.path.join(base_dir, '../aux/entsoe_tables/CO2.csv')
    file_path = os.path.abspath(file_path)  # Resolve to an absolute path

    CO2_by_gentype = {}
    with open(file_path, mode='r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            CO2_by_gentype[row['Energy Type']] = row['gCO2eq/Wh']
    return CO2_by_gentype

def get_actual_generation_by_type(country_name):
    """
    Retrieves actual electricity generation data by type for a specified country using the ENTSO-E API.
    
    Input:
        country_name (str): The name of the country for which to retrieve generation data.
    
    Output:
        dict: A dictionary mapping generation types to their respective generation values, or an error message if the request fails.
    """
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
        #logging.error(f"Key for country {country_name} not found")
        return
    country_key=entsoe_country_keys[country_name]

    params = {
        'securityToken': Config.ENTSO_E_API_KEY,
        'documentType': 'A75',  # Aggregated generation per type
        'processType': 'A16',  
        'in_Domain': country_key, # Place (entsoe_key.csv)
        'periodStart': yesterday_formatted,  # Start time (yyyymmddhhmm)
        'periodEnd': current_formatted       # End time (yyyymmddhhmm)
    }
    
    # Make the query
    response = requests.get(endpoint, params=params)

    # Transform the query response to JSON dictionary
    data_xml = response.text
    data_dict = xmltodict.parse(data_xml)
    #logging.info(json.dumps(data_dict, indent=4))
    data_json = json.loads(json.dumps(data_dict))

    # Handle the response
    if response.status_code == 200:
        #logging.info("Data has been received correctly")
        gens = {}
        time_series_list = data_json['GL_MarketDocument'].get('TimeSeries', [])
        last_up_time = yesterday_datetime
        date_format = "%Y-%m-%dT%H:%MZ"
        if isinstance(time_series_list, list) and len(time_series_list) > 0:
            #logging.info(f"Data is list")
            #get last hour
            for time_series in time_series_list:
                update_time_str = time_series['Period']['timeInterval']['end']
                update_time = datetime.strptime(update_time_str, date_format)
                if update_time > last_up_time:
                    last_up_time = update_time
            
            #logging.info(f"Last update: {last_up_time} UTC")
            last_up_time_str = last_up_time.strftime(date_format)
            #get generation by type in the last hour
            entsoe_gentype_names = load_entsoe_gentype_names()
            for time_series in time_series_list:
                if last_up_time_str == time_series['Period']['timeInterval']['end']:
                    if 'inBiddingZone_Domain.mRID' in time_series:
                        gens[entsoe_gentype_names[time_series['MktPSRType']['psrType']]] = int(time_series['Period']['Point'][-1]['quantity'])
                    else:
                        if entsoe_gentype_names[time_series['MktPSRType']['psrType']] in gens:
                            gens[entsoe_gentype_names[time_series['MktPSRType']['psrType']]] -= 0
                        else:
                            gens[entsoe_gentype_names[time_series['MktPSRType']['psrType']]] = 0
            #logging.info(gens)
            gens = {key: value for key, value in gens.items() if value != 0}
        else:
            logging.info("Data is NOT list!")

        #logging.info(gens)
        return gens
    else:
        logging.error(f"Failed to retrieve data. Status code: {response.status_code}")
        logging.error(f"Error response: {data_json}")
        return {"error": f"Failed to retrieve data. Status code: {response.status_code}"}
    
def get_CO2_from_dict(power_dict, co2_dict):
    """
    Calculates total CO2 emissions based on power generation and CO2 emission factors.
    
    Input:
        power_dict (dict): A dictionary mapping generation types to their respective power values.
        co2_dict (dict): A dictionary mapping generation types to their respective CO2 emission factors.
    
    Output:
        float: The total CO2 emissions in gCO2eq.
    """
    co2 = 0
    for key, value in power_dict.items():
        co2 += value * float(co2_dict[key])
    return co2

def entsoe_to_array(data):
    """
    Converts ENTSO-E time series data into a structured array of prices.
    
    Input:
        data (list): A list of dictionaries containing ENTSO-E time series data.
    
    Output:
        list: A structured array of prices, with missing values filled using the previous value.
    """
    max_position = max(int(item['position']) for item in data)
    
    # Initialize the result array with None values
    result = [None] * max_position

    # Fill the result array with prices, filling missing values with the previous one
    previous_value = None
    for item in data:
        position = int(item['position']) - 1  # Convert to 0-based index
        price = float(item['price.amount'])
        
        # Fill any missing positions with the previous value
        if previous_value is not None and position > 0:
            for i in range(position):
                if result[i] is None:
                    result[i] = previous_value
        
        # Set the current price and update the previous value
        result[position] = price
        previous_value = price

    # Fill any remaining None values with the previous value
    for i in range(len(result)):
        if result[i] is None:
            result[i] = previous_value

    return result

def get_price_array(country_name, type, fixed_value = 0):
    """
    Generates a price array based on the specified type (fixed or market prices).
    
    Input:
        country_name (str): The name of the country for which to retrieve prices.
        type (str): The type of price array to generate ("FIXED" or "MARKET").
        fixed_value (float, optional): The fixed price value if type is "FIXED". Defaults to 0.
    
    Output:
        list: A price array of length 24, or None if an error occurs.
    """
    # validation
    if not isinstance(country_name, str):
        logging.error(f"'country_name' should be a string, got {country_name}")
        return None
    if not isinstance(type, str):
        logging.error(f"'type' should be a string, got {type}")
        return None
    """
    try:
        fixed_value = float(fixed_value)
    except ValueError:
        logging.error(f"'fixed_value' should be a float, got {fixed_value}")
        return None
    """
    # operation
    if type == "FIXED":
        try:
            fixed_value = float(fixed_value)
            size = 24
            price_array = [fixed_value for _ in range(size)]
        except ValueError:
            logging.error(f"'fixed_value' should be a float, got {fixed_value}")
            return None
        
    elif type == "MARKET":
        prices_dict =  get_day_ahead_prices(country_name)
        price_array = entsoe_to_array(prices_dict)
        price_array = [round(value/1000, 5) for value in price_array]
    else:
        logging.error("Not valid fee type")
        return None
    return price_array

def sell_by_hours(price_array, gen_array):
    """
    Calculates the revenue from selling electricity by multiplying price and generation arrays.
    
    Input:
        price_array (list): A list of prices for each hour.
        gen_array (list): A list of generation values for each hour.
    
    Output:
        list: A list of revenue values for each hour, or None if the arrays have different lengths.
    """
    if len(price_array)!= len(gen_array):
        logging.error("Both arrays must have the same length")
        return None 
    return [a*b for a,b in zip(price_array, gen_array)]
