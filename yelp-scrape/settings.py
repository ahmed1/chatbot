# This file contains all constants and settings for yelp_restaurant_scrape.py

# Put all your keys here so you don't have to wait after reaching daily limit for one key
API_KEY1="YOUR-KEY-HERE"

# API constants
API_HOST = 'https://api.yelp.com'
SEARCH_PATH = '/v3/businesses/search'
BUSINESS_PATH = '/v3/businesses/'  # Business ID will come after slash.

# Define some globals
SEARCH_LIMIT = 5
OFFSET = 1
RATING_SORT = 'rating'
RATING_CUTOFF = 3.5
MAX_BUSINESS_COUNT_PER_CUISINE = 20
#API_CALL_COUNT = 0

# Our cities:
CITIES = {
        'new york city'
        }

# List of Yelp cuisines
# Yelp category list can be seen here:
# https://www.yelp.com/developers/documentation/v3/category_list
# The following also shows the available countries for each category:
# https://www.yelp.com/developers/documentation/v3/all_category_list
cuisines = {
        'cafes',
        'diners',
        'breakfast',
        'lunch',
        'dinner',
        'asianfusion',
        'chinese',
        'halal',
        'indian',
        'italian',
        'japanese',
        'ramen',
        'korean',
        'latin',
        'mexican',
        'mideastern',
        'noodles',
        'pakistani',
        'peruvian',
        'pizza',
        'salad',
        'sandwiches',
        'soulfood',
        'steak',
        'sushi',
        'tapas',
        'vegan',
        'vegetarian',
        'vietnamese'
}
