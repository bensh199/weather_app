"""
author: ben
reviewer:
"""

from flask import Flask, render_template, request, redirect
from weather import *
import socket
from botocore.exceptions import ClientError
import logging

app = Flask(__name__)

logging.basicConfig(level=logging.INFO, filename="WeatherLogs.log",filemode="a", format="[%(asctime)s][%(levelname)s][%(message)s]")

city = None

user_selection = {}
@app.route('/', methods=['GET', 'POST'])
def main():

    if request.method == 'GET':

        logging.info(f"A user has entered the website")

        return render_template('index.html', method="get", socket=socket.gethostname())
    
    if request.method == 'POST':
        global city

        city = request.form['city']

        data = get_weather_data(city)

        if data == "bad input":
            logging.warning(f"invalid city has been entered: {city}")
            return render_template('index.html',method="post", data=data)
        
        else:
            logging.info(f"city entered: {city}")
            return render_template('index.html',method="post", **get_weather_data(city))
        
    
@app.route("/health")
def health():
    return "ok"

@app.route("/download")
def download():
    try:
        return download_image()
    except ClientError as e:
        app.logger.error(f"S3 ClientError: {e}")
        return "Internal Server Error", 500
    
@app.route("/update-dynamodb", methods=['POST'])
def update_db():
    city = request.form['city']
    try:
        update_dynamodb(get_weather_data(city))
        return redirect('/')
    except ClientError as e:
        app.logger.error(f"S3 ClientError: {e}")
        return "Internal Server Error", 500
    
