import requests
import datetime
import boto3
from flask import Response

def geolocation(city: str):
    try:
        geolocation_json = requests.get(f"https://geocoding-api.open-meteo.com/v1/search?name={city}&count=1&language=en&format=json").json()["results"][0]
        latitude = geolocation_json["latitude"]
        longitude = geolocation_json["longitude"]
        country = geolocation_json["country"]
        city = geolocation_json["name"]

        return latitude, longitude, country, city
    except KeyError:
        return None
    

def convert_date_to_day(date_str):
    return datetime.datetime.strptime(date_str, "%Y-%m-%d").date().strftime("%A")


def convert_full_date_to_format(date_str):
    return datetime.datetime.strptime(date_str, "%Y-%m-%d").strftime("%d/%m")

def get_weather_data(city: str):
    if geolocation(city) == None:
        return "bad input"
    else:
        latitude, longitude, country, city = geolocation(city)

    weather_json: dict = requests.get(f"https://api.open-meteo.com/v1/forecast?latitude={latitude}&longitude={longitude}&hourly=temperature_2m&current=temperature_2m,relative_humidity_2m&current=temperature_2m,relative_humidity_2m&daily=temperature_2m_max,relative_humidity_2m_mean,temperature_2m_min&timezone=auto").json()
    daily_times_dates = weather_json["daily"]["time"]

    return {
        "current_temp": weather_json["current"]["temperature_2m"],
        "current_humidity": weather_json["current"]["relative_humidity_2m"],
        "week_day": [convert_date_to_day(day) for day in daily_times_dates],
        "date_stamp": [convert_full_date_to_format(day) for day in daily_times_dates],
        "daily_max_temps": weather_json["daily"]["temperature_2m_max"],
        "daily_min_temps": weather_json["daily"]["temperature_2m_min"],
        "humidity": weather_json["daily"]["relative_humidity_2m_mean"],
        "country": country,
        "city": city
    }

def download_image():
    s3_client = boto3.client('s3', region_name='il-central-1')
    obj = s3_client.get_object(Bucket="il-weather-app-bucket", Key="sky.jpg")
    return Response(obj["Body"].read(), mimetype='Content-Type',
                    headers={'Content-Disposition': 'attachment; filename=sky.jpg'})

def update_dynamodb(items):
    dynamodb = boto3.client('dynamodb', region_name='il-central-1')

    def convert_to_dynamodb_type(value):
        if isinstance(value, list):
            return {'L': [convert_to_dynamodb_type(item) for item in value]}
        elif isinstance(value, int):
            return {'N': str(value)}
        elif isinstance(value, float):
            return {'N': str(value)}
        elif isinstance(value, bool):
            return {'BOOL': value}
        else:
            return {'S': str(value)}

    for key, value in items.items():
        items[key] = convert_to_dynamodb_type(value)
    response = dynamodb.put_item(
        TableName="WeatherData",
        Item=items
    )

    return response

if __name__ == "__main__":
    update_dynamodb()
