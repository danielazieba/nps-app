from flask import render_template, request
from npsflaskapp import app

import subprocess
import json

api_key = 'FCzzTNkAX72099q1ja44eHVTYI27yOos2clMXKkT'

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


@app.route('/parks', methods=['GET','POST'])
def parks():
    keyword = request.args.get('keyword')
    return create_park_call(['', '', '', '', '', 'q=' + keyword, ''])

# parameters is an array of the following structure:
# [parkCode, stateCode, limit, start, q, fields, sort]
def create_park_call(parameters):
    park_call = 'curl -X GET "https://developer.nps.gov/api/v1/parks?'
    park_call_end = ' -H "accept: application/json"'
    park_parameters = ['']
    parameters_to_be_added = ''
    for para in parameters:
        if len(para) > 0:
            parameters_to_be_added += para
            if para != parameters[len(parameters) - 1]:
                parameters_to_be_added += '&'

    park_call += parameters_to_be_added
    park_call += 'api_key=' + api_key + '"'
    park_call += park_call_end

    return subprocess.check_output([park_call], shell=True)
#return subprocess.check_output([park_call,'api_key=',api_key,'"',park_call_end], shell=True)

