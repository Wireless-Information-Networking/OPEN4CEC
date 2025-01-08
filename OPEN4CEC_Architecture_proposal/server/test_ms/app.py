from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/', methods=['POST'])
def home():
    data = request.json
    if data and 'name' in data:
        name = data['name']
        return jsonify({"response": f"Hello {name}, from OPEN4CEC testing microservice!"})
    else:
        return jsonify({"error": "Bad Request", "message": "Missing input, no name provided"}), 400

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)

