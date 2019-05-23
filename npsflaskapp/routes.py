from flask import render_template, request
from npsflaskapp import app

import subprocess
import json

api_key = 'FCzzTNkAX72099q1ja44eHVTYI27yOos2clMXKkT'
curr_search_results = {}
curr_selected_park = ''

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
    state_selection = request.args.getlist('requestedParkStates')
    state_selection_concat = ''
    if len(keyword) > 0:
        keyword = 'q=' + keyword
    if len(state_selection) > 1:
        state_selection_concat += state_reformat(state_selection)
    elif len(state_selection) == 1:
        state_selection_concat += state_selection[0]

    if len(state_selection) > 0:
        state_selection_concat = 'stateCode=' + state_selection_concat

#return state_selection_concat
    park_result = create_park_call(['', state_selection_concat, '', '', '', keyword, ''])
    park_str = park_result.decode('utf-8')
    park_json = json.loads(park_str)
    park_names = []
    park_codes = []
    for park in park_json['data']:
        park_names.append(park['fullName'])
        park_codes.append(park['parkCode'])
    curr_search_results = park_json
    return render_template('parks.html', park_list = park_names, park_code_list = park_codes)

@app.route('/selectedpark', methods=['GET','POST'])
def selectedpark():
    desired_park_code = request.args.get('selectedCode')
    curr_selected_park = get_park_by_code(desired_park_code)
    return curr_selected_park

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

def state_reformat(state_arr):
    state_list = ''
    for i in range(len(state_arr)):
        state_list += state_arr[i]
        if state_arr[i] != state_arr[-1]:
            state_list += '%2C'
    return state_list

def get_park_by_code(park_code):
    return create_park_call(['parkCode=' + park_code, '', '', '', '', '', ''])

