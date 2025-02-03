from flask import Blueprint, request, jsonify
from app.models.CEC_model import RedisModel
import re
from datetime import datetime
import sys
import os


redis_bp = Blueprint('redis', __name__)
redis_model = RedisModel()

def complete_and_order_hours(data, default_value=0):
        
    # Generate all 24 hours in "HH:00" format
    all_hours = [(datetime(2000, 1, 1, h)).strftime("%H:00") for h in range(24)]

    # Fill missing hours with the default value
    completed_data = {hour: data.get(hour, default_value) for hour in all_hours}

    # Order the dictionary by hour
    ordered_data = dict(sorted(completed_data.items()))

    return ordered_data

def is_valid_email(email):
    # Define a regular expression for validating an email
    email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(email_regex, email) is not None
   
@redis_bp.route('/create_user', methods=['POST'])
def create_user():
    # Parse JSON input
    try:
        data = request.json
        user_email = data.get('user_email')
        user_name = data.get('user_name')
        user_password = data.get('user_password')
    except Exception as e:
        return jsonify({"error": f"Invalid input: {str(e)}"}), 400

    # Validate inputs
    if not user_email or not user_name or not user_password:
        return jsonify({"error": "Missing required fields"}), 400
    if not is_valid_email(user_email):
        return jsonify({"error": "Not a valid email provided"}), 400

    # Check if email is already registered
    
    # Create user using the model's create_user method
    try:
        response = redis_model.create_user(user_name, user_email, user_password)
        return jsonify(response), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@redis_bp.route('/add_consumption', methods=['POST'])
def add_consumption():
    try:
        data = request.json
        user_email = data['user_email']
        date = data['date']
        hour = data['hour']
        value = data['value']
    except KeyError as e:
        return jsonify({"error": f"Missing key: {str(e)}"}), 400

    try:
        response = redis_model.add_consumption(user_email, date, hour, value)
        return jsonify(response), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

@redis_bp.route('/add_production', methods=['POST'])
def add_production():
    try:
        data = request.json
        user_email = data['user_email']
        date = data['date']
        hour = data['hour']
        value = data['value']
    except KeyError as e:
        return jsonify({"error": f"Missing key: {str(e)}"}), 400

    try:
        response = redis_model.add_production(user_email, date, hour, value)
        return jsonify(response), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    
@redis_bp.route('/get_production_day', methods=['POST'])
def get_production():
    try:
        data = request.json
        user_email = data['email']
    except KeyError as e:
        return jsonify({"error": f"Missing key: {str(e)}"}), 400
    
    try:
        existing_data = redis_model.get_user(user_email)
        print(f"(Production) User data: {existing_data}", file=sys.stderr)
        if existing_data is None:
            return jsonify({"error" : "user not registered"}), 400
        else:
            current_date = datetime.now().strftime("%Y-%m-%d")
            response = redis_model.get_production_day(user_email, current_date)
            print(f"""|{os.getpid()}| [Controller] (get_production)
                  Non completed dict: {response}""", file=sys.stderr)
            response = response[0]
            response = complete_and_order_hours(response)
            print(f"(Production) Completed dict: {response}", file=sys.stderr)
            return jsonify({"hourly" : response}), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    
@redis_bp.route('/get_consumption_day', methods=['POST'])
def get_consumption():
    try:
        data = request.json
        user_email = data['email']
    except KeyError as e:
        return jsonify({"error": f"Missing key: {str(e)}"}), 400
    
    try:
        existing_data = redis_model.get_user(user_email)
        print(f"(Consumption) User data: {existing_data}", file=sys.stderr)
        if existing_data is None:
            return jsonify({"error" : "user not registered"}), 400
        else:
            current_date = datetime.now().strftime("%Y-%m-%d")
            response = redis_model.get_consumption_day(user_email, current_date)
            print(f"""|{os.getpid()}| [Controller] (get_consumption)
                  Non completed dict: {response}""", file=sys.stderr)
            response = response[0]
            response = complete_and_order_hours(response)
            print(f"(Consumption) Completed dict: {response}", file=sys.stderr)
            return jsonify({"hourly" : response}), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    
@redis_bp.route('/get_surplus_day', methods=['POST'])
def get_surplus_hourly():
    try:
        data = request.json
        user_email = data['email']
    except KeyError as e:
        return jsonify({"error": f"Missing key: {str(e)}"}), 400
    
    try:
        existing_data = redis_model.get_user(user_email)
        print(f"(Surplus) User data: {existing_data}", file=sys.stderr)
        if existing_data is None:
            return jsonify({"error" : "user not registered"}), 400
        else:
            current_date = datetime.now().strftime("%Y-%m-%d")

            consumption = redis_model.get_consumption_day(user_email, current_date)
            production = redis_model.get_production_day(user_email, current_date)

            consumption = consumption[0]
            production = production[0]

            consumption = complete_and_order_hours(consumption)
            production = complete_and_order_hours(production)

            print(f"(Surplus) cons: {consumption}, prod: {production}", file=sys.stderr)

            response = {hour: production.get(hour, 0) - consumption.get(hour, 0) for hour in set(consumption) | set(production)}

            print(f"Surplus: {response}", file=sys.stderr)

            return jsonify({"hourly" : response}), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 400