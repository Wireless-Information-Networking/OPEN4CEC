import logging
import requests
from datetime import datetime, timedelta
import xmltodict
from services.entsoe_aux import *
import json

def load_co2_by_type(file_path='entsoe_tables/CO2.csv'):
    CO2_by_gentype = {}
    with open(file_path, mode='r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            CO2_by_gentype[row['Energy Type']] = row['gCO2eq/Wh']
    return CO2_by_gentype

def get_actual_generation_by_type(ENTSO_E_API_KEY, country_name):
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
        'securityToken': ENTSO_E_API_KEY,
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
    co2 = 0
    for key, value in power_dict.items():
        co2 += value * float(co2_dict[key])
    return co2