# National Park Service App

This application is intended to provide relevant information for visitors to the many gorgeous National Park Services sites across the United States.

![Landing page](screenshots/nps-landing.png?raw=true "Landing Page")

## Features

The following features are in this app:
- Search by keyword for relevant parks
- Filter sites by state 
- View list of parks determined from search results
- Load relevant news, articles, and alerts
- View list of campgrounds at a site
- View list of visitor centers at a site
- View lesson plans, relevant people, and relevant historical locations

## Screenshots

![Search results](screenshots/nps-search-results.png?raw=true "Search Results")

![Selecting a result](screenshots/nps-selecting-a-park.png?raw=true "Site Selection")

![Viewing news](screenshots/nps-park-news.png?raw=true "Park News")

## More info

This web application was created using a Flask backend and HTML/CSS frontend. API calls for the National Park Service were generated in the Flask backend, and the resulting JSON was then parsed and displayed in a park-themed, readable manner on the application. The frontend uses Jinja2 templating and is aided by the Bulma CSS framework.

Big thanks to the NPS team for developing a fantastic API.

