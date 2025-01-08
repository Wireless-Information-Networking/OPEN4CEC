import os
import logging
from flask import Flask, request, jsonify
from dotenv import load_dotenv
from services.weather import *
from services.prices import get_day_ahead_prices
from services.gentype import *
from services.pvgen import get_PV_gen
from services.sell import *
# Configure logging to print to stdout
logging.basicConfig(level=logging.DEBUG) 

# Load .env file
load_dotenv()

# Get API key from .env
WEATHER_API_API_KEY = os.getenv('WEATHER_API_API_KEY') 
ENTSO_E_API_KEY = os.getenv('ENTSO_E_API_KEY')

app = Flask(__name__, static_folder='static', static_url_path='/')

"""================ SERVICE 1: Weather ===================="""
@app.route('/weather', methods=['POST'])
def weather():
    """
    Weather Service Endpoint

    This POST API endpoint provides weather data for a given location (latitude, longitude)
    and timezone, returning a list of weather condition image labels for the next 24 hours.
    
    The weather data is fetched using the Open-Meteo API, and sunrise/sunset times are obtained
    from WeatherAPI. The returned data includes labels indicating both the weather condition
    (based on weather codes) and whether it's day or night at the specified time.

    Request Body (JSON):
    -------------------
    - 'latitude' (float): Latitude of the location.
    - 'longitude' (float): Longitude of the location.
    - 'timezone' (str): Timezone of the location (e.g., "Europe/London").
    
    Example request body:
    {
        "latitude": 51.5074,
        "longitude": -0.1278,
        "timezone": "Europe/London"
    }
    
    Responses:
    ---------
    - 200 OK: Returns a JSON object containing the list of image labels for each hour.
    - 400 Bad Request: Returns an error message if latitude, longitude, or timezone is missing.
    - 500 Internal Server Error: Returns an error if something goes wrong on the server.

    Success Response:
    -----------------
    - JSON containing a list of image labels for weather conditions (day/night + weather code).
    Example:
    {
        "images": ["day-100", "night-200", "day-300", ...]
    }
    
    Error Responses:
    ----------------
    - If required input data is missing, the response will be:
    {
        "error": "Invalid input. Please provide latitude, longitude, and timezone."
    }
    
    - If something goes wrong during processing:
    {
        "error": "Something went wrong in server. Please try again later"
    }

    """
    data = request.json
    if 'latitude' not in data or 'longitude' not in data or 'timezone' not in data:
        return jsonify({"error": "Invalid input. Please provide latitude, longitude, and timezone."}), 400
    
    latitude = float(data['latitude'])
    longitude = float(data['longitude'])
    timezone = data['timezone']
     
    codes = get_weather(latitude, longitude, timezone)
    sunrise, sunset = get_sunrise_sunset(WEATHER_API_API_KEY, latitude, longitude)
    images = image_array(codes, sunrise, sunset)
    
    if images is None:
        return jsonify({"error": "Something went wrong in server. Please try again later"})

    return jsonify({"images": images})

"""================ SERVICE 2: Day Ahead Prices ===================="""
@app.route('/day_ahead_prices', methods=['POST'])
def day_ahead_prices():
    data = request.json
    if 'country' not in data :
        return jsonify({"error": "Invalid input. Please make sure a country is selected."}), 400
    country = data['country']

    prices = get_day_ahead_prices(ENTSO_E_API_KEY, country)
    
    if 'error' in prices:
        return jsonify(prices), 500

    return jsonify({
        'data': prices
    })

"""================ SERVICE 3: Actual Generation by Type ===================="""
@app.route('/actual_gen_type', methods=['POST'])
def actual_generation_by_type():
    data = request.json
    if 'country' not in data :
        return jsonify({"error": "Invalid input. Please make sure a country is selected."}), 400
    country = data['country']

    #logging.info(f"Searching generation data...")

    generation = get_actual_generation_by_type(ENTSO_E_API_KEY, country)

    co2_dict = load_co2_by_type()

    co2 = get_CO2_from_dict(generation, co2_dict)
    
    #logging.info(generation)
    
    if 'error' in generation:
        return jsonify(generation), 500

    return jsonify({
        'data': generation,
        'co2': co2
    })

"""================ SERVICE 4: PV POWER GENERATION ESTIMATION ===================="""
@app.route('/PVgen', methods=['POST'])
def PVgen():
    data = request.json
    if 'latitude' not in data or 'longitude' not in data or 'altitude' not in data or 'timezone' not in data:
        return jsonify({"error": "Invalid input. Please provide latitude, longitude, altitude, and timezone."}), 400

    try:
        # Convert inputs to the correct types
        latitude = float(data['latitude'])
        longitude = float(data['longitude'])
        altitude = float(data['altitude']) 
        surface = float(data['surface'])
        efficiency = float(data['efficiency'])
        tz = data['timezone']  # Timezone as a string

        power_array = get_PV_gen(latitude, longitude, altitude, surface, efficiency, tz)

        #logging.info(power_array)

        # Return GHI as an array
        return jsonify({"power": power_array})
    
    except ValueError:
        return jsonify({"error": "Something went wrong. Try again later."}), 500

"""================ SERVICE 5: SELL PRICES ===================="""
@app.route('/sell', methods=['POST'])
def sell():
    data = request.json
    if 'latitude' not in data or 'longitude' not in data or 'altitude' not in data or 'timezone' not in data:
        return jsonify({"error": "Invalid input. Please provide latitude, longitude, altitude, and timezone."}), 400
    
    try:
        latitude = float(data['latitude'])
        longitude = float(data['longitude'])
        altitude = float(data['altitude']) 
        surface = float(data['surface'])
        efficiency = float(data['efficiency'])
        tz = data['timezone']
        country = data['country']
        fee = data['fee'] 
        fixed_value = data['fixed_price']

        price_array = get_price_array(ENTSO_E_API_KEY, country, fee, fixed_value)
        power_array = get_PV_gen(latitude, longitude, altitude, surface, efficiency, tz)

        power_array = [round(value/1000, 5) for value in power_array]

        euros_by_hours = sell_by_hours(price_array, power_array)

        return jsonify({"sell": euros_by_hours})
    
    except ValueError:
        return jsonify({"error": "Something went wrong. Try again later."}), 500

"""================ MAIN ===================="""
@app.route('/')
def index():
    return app.send_static_file('index.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)