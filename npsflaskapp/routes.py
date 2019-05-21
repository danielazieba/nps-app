from flask import render_template, request
from npsflaskapp import app

import subprocess

@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html')

@app.route('/alerts')
def alerts():
    subprocess_output = subprocess.check_output(['curl -X GET "https://developer.nps.gov/api/v1/alerts?stateCode=KY&api_key=FCzzTNkAX72099q1ja44eHVTYI27yOos2clMXKkT" -H "accept: application/json"'], shell=True)
    return subprocess_output

@app.route('/campgrounds', methods=['GET','POST'])
def campgrounds():
    selection = request.args.getlist('requestedStates')
    subprocess_output = subprocess.check_output(['curl -X GET "https://developer.nps.gov/api/v1/campgrounds?stateCode=KY%2CAL%2CFL&api_key=FCzzTNkAX72099q1ja44eHVTYI27yOos2clMXKkT" -H "accept: application/json"'], shell=True)
    return render_template('campgrounds.html', campground_list = subprocess_output)
