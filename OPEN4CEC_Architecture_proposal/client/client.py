import requests

url = 'https://sirienergy.uab.cat/test_ms'

headers = {
    "Content-Type": "application/json",
    "API-Key": "my-valid-api-key"
}

data = {"name": "User"}

try:
    response = requests.post(url, headers=headers, json=data)

    if response.status_code == 200:
        correct_response = response.json().get("response", "No response message found")
        print(correct_response)
    else:
        error = response.json().get("error", "Unknown error")
        message = response.json().get("message", "No message provided")
        print(f"Error: {error}")
        print(f"Message: {message}")

except requests.exceptions.RequestException as e:
    print(f"Connection error: {e}")


