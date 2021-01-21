import requests
from datetime import datetime
import json

# 使用和风天气提供的api获得天气数据

KEY = "d32b19030e1f482ab208634dc9c8ef36"
now_weather_api = "https://devapi.qweather.com/v7/weather/now"
three_days_weather_api = "https://devapi.qweather.com/v7/weather/3d"
location_id_api = "https://geoapi.qweather.com/v2/city/lookup"


def get_location_id(address):
    result = json.loads(requests.get(location_id_api, params={"location":address, "key":KEY}).text)
    if result['code'] == "200":
        id = result['location'][0]['id']
        return id
    else:
        print("api无法访问！")

def get_weather_now(address):
    result = json.loads(requests.get(now_weather_api, params={
        "location": get_location_id(address),
        "key": KEY
    }).text)
    if result['code'] == "200":
        return result['now']
    else:
        print("api无法访问！")

def get_weather_three_days(address):
    result = json.loads(requests.get(three_days_weather_api, params={
        "location": get_location_id(address),
        "key": KEY
    }).text)
    if result['code'] == '200':
        return result["daily"]
    else:
        print("api无法访问！")

def get_weather_by_day(address, date):
    date_str = datetime.strftime(date, "%Y-%m-%d")
    result = get_weather_three_days(address)
    for item in result:
        if item['fxDate'] == date_str:
            return item
