# This file contains all constants and settings for yelp_restaurant_scrape.py

# Put your Yelp API key in a file called 'creds.txt'
API_KEY_LOCATION = 'creds.txt'
API_KEY = open(API_KEY_LOCATION, 'r').read().replace('\n','')

# API constants
API_HOST = 'https://api.yelp.com'
SEARCH_PATH = '/v3/businesses/search'
BUSINESS_PATH = '/v3/businesses/'  # Business ID will come after slash.

# Define some globals
SEARCH_LIMIT = 10
OFFSET = 1
RATING_SORT = 'rating'
RATING_CUTOFF = 3.5
MAX_BUSINESS_COUNT_PER_CUISINE = 20 # later, change to 1100

# Cities: (add more later if we want to expand)
CITIES = {
        'new york city'
        }

# List of Yelp cuisines
# Yelp category list can be seen here:
# https://www.yelp.com/developers/documentation/v3/category_list
# The following also shows the available countries for each category:
# https://www.yelp.com/developers/documentation/v3/all_category_list
cuisines = {
        'chinese',
        'indian',
        'italian',
        'burgers',
        'pizza'
}
