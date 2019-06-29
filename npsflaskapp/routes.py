from flask import render_template, request, jsonify
from npsflaskapp import app

import subprocess
import json

api_key = '' # to run this, get an API key and put it here
curr_search_results = {}
curr_selected_park = ''

@app.route('/')
@app.route('/index')
def index():
    with open('data/states.json') as json_file:
        data = json.load(json_file)
    return render_template('index.html', states=data)

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

    park_result = create_park_call(['', state_selection_concat, '', '', '', keyword, ''])
    park_str = park_result.decode('utf-8')
    park_json = json.loads(park_str)
    park_names = []
    park_codes = []
    park_designation = []
    park_states = []
    for park in park_json['data']:
        park_names.append(park['fullName'])
        park_codes.append(park['parkCode'])
        park_designation.append(park['designation'])
        park_states.append(park['states'])
    curr_search_results = park_json
    return render_template('parks.html', park_list = park_names, park_code_list = park_codes, states = park_states, designation = park_designation)

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

@app.route('/newsstand', methods=['GET','POST'])
def newsstand():
    feed = ''
    feed_type = ''
    desired_park_code = request.args.get('parkAlert')
    curr_selected_park = get_park_by_code(desired_park_code)
    selected_str = curr_selected_park.decode('utf-8')
    selected_json = json.loads(selected_str)
    selected_park = selected_json['data'][0]
    return render_template('newsstand.html', park_name=selected_park['fullName'], park_code=desired_park_code, display_type=feed_type)

@app.route('/alerts', methods=['GET','POST'])
def alerts():
    desired_park_code = request.args.get('parkAlerts')
    curr_park_name = get_park_by_code(desired_park_code)
    selected_park = curr_park_name.decode('utf-8')
    park_json = json.loads(selected_park)
    
    park_alert_data = create_alert_call('parkCode=' + desired_park_code)
    selected_str = park_alert_data.decode('utf-8')
    alert_json = json.loads(selected_str)
    alert_desc = []
    alert_names = []
    alert_categories = []
    alert_urls = []
    for alert in alert_json['data']:
        alert_names.append(alert['title'])
        alert_desc.append(alert['description'])
        alert_categories.append(alert['category'])
        alert_urls.append(alert['url'])
    return render_template('alerts.html',
                           alert_list=alert_names,
                           desc=alert_desc,
                           park_name=park_json['data'][0]['fullName'],
                           category=alert_categories,
                           urls=alert_urls,
                           park_code=desired_park_code)

@app.route('/articles', methods=['GET','POST'])
def articles():
    desired_park_code = request.args.get('parkArticles')
    curr_park_name = get_park_by_code(desired_park_code)
    selected_park = curr_park_name.decode('utf-8')
    park_json = json.loads(selected_park)
    
    park_article_data = create_call('parkCode=' + desired_park_code, 'articles')
    selected_str = park_article_data.decode('utf-8')
    article_json = json.loads(selected_str)
    article_desc = []
    article_names = []
    article_urls = []
    for article in article_json['data']:
        article_names.append(article['title'])
        article_desc.append(article['listingdescription'])
        article_urls.append(article['url'])
    return render_template('articles.html',
                           article_list=article_names,
                           desc=article_desc,
                           park_name=park_json['data'][0]['fullName'],
                           urls=article_urls,
                           park_code=desired_park_code)

@app.route('/education', methods=['GET','POST'])
def education():
    desired_park_code = request.args.get('educationWant')
    curr_selected_park = get_park_by_code(desired_park_code)
    selected_str = curr_selected_park.decode('utf-8')
    selected_json = json.loads(selected_str)
    selected_park = selected_json['data'][0]
    return render_template('education.html', park_name = selected_park['fullName'], park_code=desired_park_code)

@app.route('/lessons', methods=['GET','POST'])
def lessons():
    desired_park_code = request.args.get('parkLessons')
    curr_park_name = get_park_by_code(desired_park_code)
    selected_park = curr_park_name.decode('utf-8')
    park_json = json.loads(selected_park)
    
    park_lesson_data = create_lesson_call('parkCode=' + desired_park_code)
    selected_str = park_lesson_data.decode('utf-8')
    lesson_json = json.loads(selected_str)
    lesson_desc = []
    lesson_names = []
    lesson_topics = []
    lesson_grades = []
    lesson_urls = []
    for lesson in lesson_json['data']:
        lesson_names.append(lesson['title'])
        lesson_desc.append(lesson['questionobjective'])
        lesson_topics.append(lesson['subject'])
        lesson_grades.append(lesson['gradelevel'])
        lesson_urls.append(lesson['url'])
    return render_template('lessons.html',
                           lesson_list=lesson_names,
                           desc=lesson_desc,
                           park_name=park_json['data'][0]['fullName'],
                           subjects=lesson_topics,
                           grade=lesson_grades,
                           urls=lesson_urls,
                           park_code=desired_park_code)

@app.route('/people', methods=['GET','POST'])
def people():
    desired_park_code = request.args.get('parkPeople')
    curr_park_name = get_park_by_code(desired_park_code)
    selected_park = curr_park_name.decode('utf-8')
    park_json = json.loads(selected_park)
    
    park_people_data = create_people_call('parkCode=' + desired_park_code)
    selected_str = park_people_data.decode('utf-8')
    people_json = json.loads(selected_str)
    people_desc = []
    people_names = []
    people_imgs = []
    people_urls = []
    for person in people_json['data']:
        people_names.append(person['title'])
        people_desc.append(person['listingdescription'])
        people_imgs.append(person['listingimage']['url'])
        people_urls.append(person['url'])
    return render_template('people.html',
                           people_list=people_names,
                           desc=people_desc,
                           park_name=park_json['data'][0]['fullName'],
                           image_urls=people_imgs,
                           urls=people_urls,
                           park_code=desired_park_code)

@app.route('/news', methods=['GET','POST'])
def news():
    desired_park_code = request.args.get('parkNews')
    curr_park_name = get_park_by_code(desired_park_code)
    selected_park = curr_park_name.decode('utf-8')
    park_json = json.loads(selected_park)
    
    park_news_data = create_call('parkCode=' + desired_park_code, 'newsreleases')
    
    
    selected_str = park_news_data.decode('utf-8')
    news_json = json.loads(selected_str)
    news_desc = []
    news_names = []
    news_urls = []
    news_dates = []
    for news in news_json['data']:
        news_names.append(news['title'])
        news_desc.append(news['abstract'])
        news_urls.append(news['url'])
        news_dates.append(news['releasedate'])
    return render_template('news.html',
                           news_list=news_names,
                           park_name=park_json['data'][0]['fullName'],
                           desc=news_desc,
                           urls=news_urls,
                           date=news_dates,
                           park_code=desired_park_code)


@app.route('/places', methods=['GET','POST'])
def places():
    desired_park_code = request.args.get('parkPlaces')
    curr_park_name = get_park_by_code(desired_park_code)
    selected_park = curr_park_name.decode('utf-8')
    park_json = json.loads(selected_park)
    
    park_places_data = create_places_call('parkCode=' + desired_park_code)
    selected_str = park_places_data.decode('utf-8')
    places_json = json.loads(selected_str)
    places_desc = []
    places_names = []
    places_imgs = []
    places_urls = []
    for place in places_json['data']:
        places_names.append(place['title'])
        places_desc.append(place['listingdescription'])
        places_imgs.append(place['listingimage']['url'])
        places_urls.append(place['url'])
    return render_template('places.html',
                          places_list=places_names,
                          park_name=park_json['data'][0]['fullName'],
                          desc=places_desc,
                          urls=places_urls,
                          image_urls=places_imgs,
                          park_code=desired_park_code)

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

def create_alert_call(parameters):
    alert_call = 'curl -X GET "https://developer.nps.gov/api/v1/alerts?'
    alert_call_end = ' -H "accept: application/json"'
    alert_call += parameters + '&'
    alert_call += 'api_key=' + api_key + '"'
    alert_call += alert_call_end
    
    return subprocess.check_output([alert_call], shell=True)

def create_article_call(parameters):
    alert_call = 'curl -X GET "https://developer.nps.gov/api/v1/articles?'
    alert_call_end = ' -H "accept: application/json"'
    alert_call += parameters + '&'
    alert_call += 'api_key=' + api_key + '"'
    alert_call += alert_call_end
    
    return subprocess.check_output([alert_call], shell=True)

def create_lesson_call(parameters):
    alert_call = 'curl -X GET "https://developer.nps.gov/api/v1/lessonplans?'
    alert_call_end = ' -H "accept: application/json"'
    alert_call += parameters + '&'
    alert_call += 'api_key=' + api_key + '"'
    alert_call += alert_call_end
    
    return subprocess.check_output([alert_call], shell=True)

def create_people_call(parameters):
    alert_call = 'curl -X GET "https://developer.nps.gov/api/v1/people?'
    alert_call_end = ' -H "accept: application/json"'
    alert_call += parameters + '&'
    alert_call += 'api_key=' + api_key + '"'
    alert_call += alert_call_end
    
    return subprocess.check_output([alert_call], shell=True)

def create_places_call(parameters):
    place_call = 'curl -X GET "https://developer.nps.gov/api/v1/places?'
    place_call_end = ' -H "accept: application/json"'
    place_call += parameters + '&'
    place_call += 'api_key=' + api_key + '"'
    place_call += place_call_end
    
    return subprocess.check_output([place_call], shell=True)

def create_call(park_name, type):
    place_call = 'curl -X GET "https://developer.nps.gov/api/v1/' + type + '?'
    place_call_end = ' -H "accept: application/json"'
    place_call += park_name + '&'
    place_call += 'api_key=' + api_key + '"'
    place_call += place_call_end
    
    return subprocess.check_output([place_call], shell=True)

def state_reformat(state_arr):
    state_list = ''
    for i in range(len(state_arr)):
        state_list += state_arr[i]
        if state_arr[i] != state_arr[-1]:
            state_list += '%2C'
    return state_list

def get_park_by_code(park_code):
    return create_park_call(['parkCode=' + park_code, '', '', '', '', '', ''])

