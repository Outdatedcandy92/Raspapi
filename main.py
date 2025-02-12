from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uuid
import json
import os
import secrets
import requests
import xmltodict

app = FastAPI()

USER_DATA_FILE = "users.json"

if os.path.exists(USER_DATA_FILE):
    with open(USER_DATA_FILE, "r") as file:
        users = json.load(file)
else:
    users = {}

class UserSignup(BaseModel):
    email: str
    password: str

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
    
    return {"message": "User signed up successfully", "bearer_token": bearer_token}

@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.get("/routes")
async def get_routes():
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
