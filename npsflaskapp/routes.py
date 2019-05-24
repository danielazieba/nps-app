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
    selected_str = curr_selected_park.decode('utf-8')
    selected_json = json.loads(selected_str)
    selected_park = selected_json['data'][0]
    return render_template('selected.html', park_name = selected_park['fullName'],
                           park_state = selected_park['states'],
                           park_desc = selected_park['description'],
                           park_location = selected_park['latLong'],
                           park_designation = selected_park['designation'],
                           selected_code = desired_park_code)

@app.route('/selectedcamp', methods=['GET','POST'])
def selectedcamp():
    desired_park_code = request.args.get('campgroundWanted')
    curr_camps = create_campsite_call('parkCode=' + desired_park_code)
    selected_str = curr_camps.decode('utf-8')
    selected_json = json.loads(selected_str)
    camp_names = []
    camp_weather = 'Weather data unavailable.'
    if len(selected_json['data']) > 0:
        camp_weather = selected_json['data'][0]['weatheroverview']
    internet_info = []
    accessibility_info = []
    for campsite in selected_json['data']:
        camp_names.append(campsite['name'])
        if len(campsite['accessibility']['internetinfo']) > 0:
            internet_info.append(campsite['accessibility']['internetinfo'])
        else:
            internet_info.append('Not available')
        accessibility_info.append(campsite['accessibility']['wheelchairaccess'])
    return render_template('selected_amenities.html',
                           campground_list=camp_names,
                           weather=camp_weather,
                           internet=internet_info,
                           ada_info=accessibility_info)

@app.route('/parkmap', methods=['GET','POST'])
def parkmap():
    park_code = request.args.get('parkMap')
    return render_template('parkmap.html', park_map = 'https://www.nps.gov/carto/hfc/carto/media/'
                           + park_code + 'map1.jpg')

@app.route('/visitorcenters', methods=['GET','POST'])
def visitorcenters():
    park_code = request.args.get('vcWanted')
    curr_park_name = get_park_by_code(park_code)
    selected_park = curr_park_name.decode('utf-8')
    vc_park = json.loads(selected_park)
    
    park_centers = create_vc_call('parkCode=' + park_code)
    selected_str = park_centers.decode('utf-8')
    vc_json = json.loads(selected_str)
    vc_locations = []
    vc_desc = []
    vc_names = []
    vc_nps_links = []
    vc_dirs = []
    for vc in vc_json['data']:
        vc_names.append(vc['name'])
        vc_locations.append(vc['latLong'])
        vc_desc.append(vc['description'])
        vc_dirs.append(vc['directionsInfo'])
        vc_nps_links.append(vc['url'])
    return render_template('visitorcenters.html',
                           vc_list=vc_names,
                           location=vc_locations,
                           desc=vc_desc,
                           dir=vc_dirs,
                           urls=vc_nps_links,
                           park_name=vc_park['data'][0]['fullName'])


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

def create_campsite_call(parameters):
    camp_call = 'curl -X GET "https://developer.nps.gov/api/v1/campgrounds?'
    camp_call_end = ' -H "accept: application/json"'
    camp_call += parameters + '&'
    camp_call += 'api_key=' + api_key + '"'
    camp_call += camp_call_end
    
    return subprocess.check_output([camp_call], shell=True)

def create_vc_call(parameters):
    camp_call = 'curl -X GET "https://developer.nps.gov/api/v1/visitorcenters?'
    camp_call_end = ' -H "accept: application/json"'
    camp_call += parameters + '&'
    camp_call += 'api_key=' + api_key + '"'
    camp_call += camp_call_end
    
    return subprocess.check_output([camp_call], shell=True)

def state_reformat(state_arr):
    state_list = ''
    for i in range(len(state_arr)):
        state_list += state_arr[i]
        if state_arr[i] != state_arr[-1]:
            state_list += '%2C'
    return state_list

def get_park_by_code(park_code):
    return create_park_call(['parkCode=' + park_code, '', '', '', '', '', ''])

