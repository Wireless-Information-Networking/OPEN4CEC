from flask import Blueprint, request, jsonify, render_template
from app.models.weather_model import get_weather, get_sunrise_sunset, image_array

weather_bp = Blueprint('weather', __name__)

@weather_bp.route('/weather', methods=['POST'])
def weather():
    data = request.json
    if 'latitude' not in data or 'longitude' not in data or 'timezone' not in data:
        return jsonify({"error": "Invalid input. Please provide latitude, longitude, and timezone."}), 400

    latitude = float(data['latitude'])
    longitude = float(data['longitude'])
    timezone = data['timezone']

    try:
        codes = get_weather(latitude, longitude, timezone)
        sunrise, sunset = get_sunrise_sunset(latitude, longitude)
        images = image_array(codes, sunrise, sunset)
        return render_template('weather_images.html', images=images)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
