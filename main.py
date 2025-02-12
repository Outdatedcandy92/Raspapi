from fastapi import FastAPI
import requests
import xmltodict
import json

app = FastAPI()

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
    
    # Extract routes and transform the data
    routes = data_dict['body']['route']
    transformed_routes = [
        {"route": route["@tag"], "title": route["@title"]}
        for route in routes
    ]
    
    return {"routes": transformed_routes}

@app.get("/routeInfo")
async def get_route_config(r: str):
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