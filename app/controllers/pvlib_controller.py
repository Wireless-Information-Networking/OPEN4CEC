from flask import Blueprint, request, jsonify
from app.models.pvlib_model import *

pvlib_bp = Blueprint('pvlib', __name__)

@pvlib_bp.route('/PVgen', methods=['POST'])
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
