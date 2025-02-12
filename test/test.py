import requests

# URL of the FastAPI server
url = "http://localhost:8000/signup"

# User data to sign up
user_data = {
    "email": "user@1example.com",
    "password": "securepassword"
}

# Send POST request to sign up
response = requests.post(url, json=user_data)

# Print the response
print(response.json())