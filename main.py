from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
import uuid
import json
import os
import secrets
import requests
import xmltodict
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

app = FastAPI()

# Mount static files at /static
app.mount("/static", StaticFiles(directory="static", html=True), name="static")

# Serve index.html when someone visits "/"
@app.get("/")
async def serve_index():
    return FileResponse("static/index.html")



USER_DATA_FILE = "users.json"
TOKENS_FILE = "tokens.json"

if os.path.exists(USER_DATA_FILE):
    with open(USER_DATA_FILE, "r") as file:
        users = json.load(file)
else:
    users = {}

if os.path.exists(TOKENS_FILE):
    with open(TOKENS_FILE, "r") as file:
        tokens = json.load(file)
else:
    tokens = {}

class UserSignup(BaseModel):
    email: str
    password: str

class UserRoute(BaseModel):
    route: str

security = HTTPBearer()

def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    if token not in tokens.values():
        raise HTTPException(status_code=403, detail="Invalid or expired token")
    return token


@app.post("/signup")
async def signup(user: UserSignup):
    if user.email in users:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    user_id = str(uuid.uuid4())
    bearer_token = secrets.token_hex(16)
    
    users[user.email] = {
        "user_id": user_id,
        "password": user.password,
        "bearer_token": bearer_token
    }
    
    with open(USER_DATA_FILE, "w") as file:
        json.dump(users, file)
    
    tokens[user_id] = bearer_token
    with open(TOKENS_FILE, "w") as file:
        json.dump(tokens, file)
    
    return {"message": "User signed up successfully", "bearer_token": bearer_token}

# Add a route to the user's data
@app.post("/add_route")
async def add_route(user_route: UserRoute, token: str = Depends(verify_token)):
    user_id = next((uid for uid, tkn in tokens.items() if tkn == token), None)
    if not user_id:
        raise HTTPException(status_code=403, detail="Invalid or expired token")
    
    user_email = next((email for email, data in users.items() if data["user_id"] == user_id), None)
    if not user_email:
        raise HTTPException(status_code=404, detail="User not found")
    
    users[user_email]["route"] = user_route.route
    
    with open(USER_DATA_FILE, "w") as file:
        json.dump(users, file)
    
    return {"message": "Route added successfully"}

# Remove a route from the user's data
@app.get("/remove_route")
async def remove_route(token: str = Depends(verify_token)):
    user_id = next((uid for uid, tkn in tokens.items() if tkn == token), None)
    if not user_id:
        raise HTTPException(status_code=403, detail="Invalid or expired token")
    
    user_email = next((email for email, data in users.items() if data["user_id"] == user_id), None)
    if not user_email:
        raise HTTPException(status_code=404, detail="User not found")
    
    if "route" in users[user_email]:
        del users[user_email]["route"]
    
    with open(USER_DATA_FILE, "w") as file:
        json.dump(users, file)
    
    return {"message": "Route removed successfully"}





# Get a list of routes
@app.get("/routes")
async def get_routes(token: str = Depends(verify_token)):
    url = "https://retro.umoiq.com/service/publicXMLFeed?command=routeList&a=ttc"
    headers = {
        "Accept-Encoding": "gzip, deflate"
    }
    response = requests.get(url, headers=headers)
    data_dict = xmltodict.parse(response.content)
    
    routes = data_dict['body']['route']
    transformed_routes = [
        {"route": route["@tag"], "title": route["@title"]}
        for route in routes
    ]
    
    return {"routes": transformed_routes}

# Get information about a specific route
@app.get("/route_info")
async def get_route_info(r: str = None, token: str = Depends(verify_token)):
    user_id = next((uid for uid, tkn in tokens.items() if tkn == token), None)
    if not user_id:
        raise HTTPException(status_code=403, detail="Invalid or expired token")
    
    user_email = next((email for email, data in users.items() if data["user_id"] == user_id), None)
    if not user_email:
        raise HTTPException(status_code=404, detail="User not found")
    
    if r is None:
        if "route" not in users[user_email]:
            raise HTTPException(status_code=400, detail="No route provided and no default route set for user")
        r = users[user_email]["route"]
    
    url = f"https://retro.umoiq.com/service/publicXMLFeed?command=routeConfig&a=ttc&r={r}"
    headers = {
        "Accept-Encoding": "gzip, deflate"
    }
    response = requests.get(url, headers=headers)
    data_dict = xmltodict.parse(response.content)
    
    route_info = data_dict['body']['route']
    transformed_route_info = {
        key.lstrip('@'): value for key, value in route_info.items()
    }
    if 'stop' in transformed_route_info:
        transformed_route_info['stop'] = [
            {key.lstrip('@'): value for key, value in stop.items()}
            for stop in transformed_route_info['stop']
        ]
    
    return transformed_route_info


@app.get("/predictions")
async def get_predictions(s: str, rt: str = None, token: str = Depends(verify_token)):
    user_id = next((uid for uid, tkn in tokens.items() if tkn == token), None)
    if not user_id:
        raise HTTPException(status_code=403, detail="Invalid or expired token")
    
    user_email = next((email for email, data in users.items() if data["user_id"] == user_id), None)
    if not user_email:
        raise HTTPException(status_code=404, detail="User not found")
    
    if rt:
        url = f"https://retro.umoiq.com/service/publicXMLFeed?command=predictions&a=ttc&stopId={s}&routeTag={rt}"
    else:
        if "route" in users[user_email]:
            route = users[user_email]["route"]
            url = f"https://retro.umoiq.com/service/publicXMLFeed?command=predictions&a=ttc&stopId={s}&routeTag={route}"
        else:
            url = f"https://retro.umoiq.com/service/publicXMLFeed?command=predictions&a=ttc&stopId={s}"
    
    headers = {
        "Accept-Encoding": "gzip, deflate"
    }
    response = requests.get(url, headers=headers)
    response_data = xmltodict.parse(response.content)

    predictions = response_data['body']
    if '@copyright' in predictions:
        del predictions['@copyright']
    
    def transform_keys(obj):
        if isinstance(obj, dict):
            new_obj = {}
            for key, value in obj.items():
                new_key = key.lstrip('@')
                new_obj[new_key] = transform_keys(value)
            return new_obj
        elif isinstance(obj, list):
            return [transform_keys(item) for item in obj]
        else:
            return obj
    
    transformed_predictions = transform_keys(predictions)
    
    if 'predictions' in transformed_predictions:
        for prediction in transformed_predictions['predictions']:
            if 'direction' in prediction:
                prediction['direction'] = transform_keys(prediction['direction'])
            keys_to_remove = ['agencyTitle', 'routeTitle', 'routeTag', 'stopTitle', 'stopTag']
            for key in keys_to_remove:
                if key in prediction:
                    del prediction[key]
    
    return transformed_predictions