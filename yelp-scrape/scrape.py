# -*- coding: utf-8 -*-
"""
All constants/globals (e.g., CUISINES list, RATING_CUTOFF, SEARCH_LIMIT, etc.)
are located in settings.py and can be modified there.
"""

from __future__ import print_function
from settings import *  # has all globals
import json
import requests
import sys

# This client code can run on Python 2.x or 3.x.  Your imports can be
# simpler if you only need one of those.

# For Python 3.0 and later
from urllib.error import HTTPError

def read_from_json():
    filename = "db.json"
    with open(filename, 'r') as read_file:
        db = json.load(read_file)
    return db

def write_to_json(dic):
    filename = "db-test.json"
    with open(filename, 'w') as write_file:
        json.dump(dic, write_file, indent=2)

# TODO: generalize open/close file functions
def open_file(file):
    filename = file + ".json"
    with open(filename, 'r') as read_file:
        memo = json.load(read_file)
        return memo


def build_item_dic(biz, cuisine):
    item = {}
    biz_record = {"PutRequest": {"Item": item}}

    item["BusinessId"] = {"S": biz["id"]}
    item["Address"] = {"S": biz["location"]["display_address"][0]}
    item["Cuisine"] = {"S": cuisine}
    item["Name"] = {"S": biz["name"]}
    item["NumReviews"] = {"N": biz["review_count"]}
    item["Rating"] = {"N": biz["rating"]}
    item["Zipcode"] = {"N": biz["location"]["zip_code"]}
    item["Latitude"] = {"N": biz["coordinates"]["latitude"]}
    item["Longitude"] = {"N": biz["coordinates"]["longitude"]}

    biz_record["PutRequest"]["Item"] = item
    return biz_record

def main():
    # before this, must run
    db = read_from_json() # dict is copy of db
    headers = {'Authorization': 'Bearer %s' % API_KEY}

    #print(json.dumps(db, indent=2))
    #print(db["yelp-restaurants"][0]["PutRequest"]["Item"])
    #exit(1)
    try:
        for cuisine in cuisines:
            print("Printing %s cuisine:" % cuisine)
            current_offset = OFFSET # always starts at OFFSET but increments by SEARCH_LIMIT after every request
            PARAMS = {
                'categories': cuisine,
                'location': 'New York City',
                'offset': current_offset,
                'limit': SEARCH_LIMIT
            }
            r = requests.get(url=API_HOST + SEARCH_PATH, params=PARAMS, headers=headers)
            parsed = json.loads(r.text)
            #print(json.dumps(parsed, indent=2))

            total_num_businesses = parsed["total"]
            total_num_pages = total_num_businesses // SEARCH_LIMIT
            #print(total_num_businesses)

            num_businesses_this_cuisine_stored = 0

            # Each i is a new request and page
            for i in range(1, total_num_pages + 1) :



                print("num businesses for this cuisine is %s " % num_businesses_this_cuisine_stored)
                if num_businesses_this_cuisine_stored >= MAX_BUSINESS_COUNT_PER_CUISINE:
                    break
                r = requests.get(url=API_HOST + SEARCH_PATH, params=PARAMS, headers=headers)
                parsed = json.loads(r.text)

                restaurants = {}
                # Check total_num_pages - 1 so that we don't have to deal with num records on last page
                for biz in parsed["businesses"]:

                    # TODO: use a memo list or dictionary to check if business has already been written
                    # the list of processed businesses should be stored in a separate file so it persists
                    #if biz["id"] in memo["processed_biz_ids"]:
                    #    continue

                    if ((i == total_num_pages - 1) or \
                            (num_businesses_this_cuisine_stored >= MAX_BUSINESS_COUNT_PER_CUISINE)):
                        break

                    num_businesses_this_cuisine_stored += 1
                    #print(json.dumps(biz, indent=2))
                    #print("Current restaurant: %s " % biz["name"])
                    item = build_item_dic(biz, cuisine)
                    print(json.dumps(item, indent=2))
                    #write_to_json(item) # TODO: append to json
                PARAMS['offset'] += SEARCH_LIMIT

    # Once we figure out schema, do something like this:
    except KeyboardInterrupt:
        write_to_json(item)

    except HTTPError as error:
        sys.exit(
            'Encountered HTTP error {0} on {1}:\n {2}\nAbort program.'.format(
                error.code,
                error.url,
                error.read(),
            )
        )

if __name__ == '__main__':
    main()
