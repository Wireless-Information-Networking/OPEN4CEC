from flask import Blueprint, request, jsonify
from app.models.ENTSOE_models import *

entsoe_bp = Blueprint('entsoe', __name__)

@entsoe_bp.route('/day_ahead_prices', methods=['POST'])
def day_ahead_prices():
    data = request.json
    if 'country' not in data :
        return jsonify({"error": "Invalid input. Please make sure a country is selected."}), 400
    country = data['country']

    prices = get_day_ahead_prices(country)
    
    if 'error' in prices:
        return jsonify(prices), 500

    return jsonify({
        'data': prices
    })

@entsoe_bp.route('/actual_gen_type', methods=['POST'])
def actual_generation_by_type():
    data = request.json
    if 'country' not in data :
        return jsonify({"error": "Invalid input. Please make sure a country is selected."}), 400
    country = data['country']

    #logging.info(f"Searching generation data...")

    generation = get_actual_generation_by_type(country)

    co2_dict = load_co2_by_type()

    co2 = get_CO2_from_dict(generation, co2_dict)
    
    #logging.info(generation)
    
    if 'error' in generation:
        return jsonify(generation), 500

    return jsonify({
        'data': generation,
        'co2': co2
    })