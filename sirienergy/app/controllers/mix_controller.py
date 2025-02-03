from flask import Blueprint, request, jsonify
from app.models.ENTSOE_models import *
from app.models.pvlib_model import *
import logging

mix_bp = Blueprint('mix', __name__)

@mix_bp.route('/sell', methods=['POST'])
def sell():
    logging.info("Tamos en sell")
    print("print")
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

        price_array = get_price_array(country, fee, fixed_value)
        logging.info(f"Price array{price_array}")
        power_array = get_PV_gen(latitude, longitude, altitude, surface, efficiency, tz)
        logging.info(f"Power array{power_array}")
        print("Ahora si q quiere ir con prints xdn't")
        power_array = [round(value/1000, 5) for value in power_array]

        euros_by_hours = sell_by_hours(price_array, power_array)

        return jsonify({"sell": euros_by_hours})
    
    except ValueError:
        return jsonify({"error": "Something went wrong. Try again later."}), 500
