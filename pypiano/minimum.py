'''RGB値をESPに送信する最小のコード'''
import requests
import json

# ESP server URL with the correct endpoint
esp_url = "http://10.42.0.184:5000/ws"

# Color data to send
color_data = {
    "r": 255,
    "g": 100,
    "b": 50
}

try:
    # Sending POST request to the ESP
    headers = {'Content-Type': 'application/json'}
    response = requests.post(esp_url, headers=headers, json=color_data)

    # Print the response from the server
    if response.status_code == 200:
        print("Successfully sent color data:", response.text)
    else:
        print(f"Failed to send color data. Status code: {response.status_code}")
except requests.exceptions.RequestException as e:
    print(f"Error sending data to ESP: {e}")
