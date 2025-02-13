import requests
import json

token = "304bdca26ef54dec0043b6eaddef65f6"

def routeinfo():
    url = "http://localhost:8000/route_info?r=11"
    headers = {
        "Authorization": f"Bearer {token}"
    }

    response = requests.get(url, headers=headers)

    with open('response.json', 'w') as json_file:
        json.dump(response.json(), json_file, indent=4)

    print("Response saved to response.json")

def add_route():
    url = "http://localhost:8000/add_route"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    data = {
        "route": "34"
    }

    response = requests.post(url, headers=headers, json=data)

    with open('add_route_response.json', 'w') as json_file:
        json.dump(response.json(), json_file, indent=4)

    print("Response saved to add_route_response.json")

#routeinfo()
add_route()