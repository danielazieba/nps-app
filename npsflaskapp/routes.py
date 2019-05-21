from flask import render_template, request
from npsflaskapp import app

import subprocess
import json

@app.route('/')
@app.route('/index')
def index():
    with open('data/states.json') as json_file:
        data = json.load(json_file)
    return render_template('index.html', states=data)

@app.route('/alerts')
def alerts():
    subprocess_output = subprocess.check_output(['curl -X GET "https://developer.nps.gov/api/v1/alerts?stateCode=KY&api_key=FCzzTNkAX72099q1ja44eHVTYI27yOos2clMXKkT" -H "accept: application/json"'], shell=True)
    return subprocess_output

@app.route('/campgrounds', methods=['GET','POST'])
def campgrounds():
    selection = request.args.getlist('requestedStates')
    subprocess_output = subprocess.check_output(['curl -X GET "https://developer.nps.gov/api/v1/campgrounds?stateCode=KY%2CAL%2CFL&api_key=FCzzTNkAX72099q1ja44eHVTYI27yOos2clMXKkT" -H "accept: application/json"'], shell=True)
    campground_str = subprocess_output.decode('utf-8')
    campground_json = json.loads(campground_str)
    campground_names = []
    for campground in campground_json['data']:
        campground_names.append(campground['name'])
    return render_template('campgrounds.html', campground_list = campground_names)
