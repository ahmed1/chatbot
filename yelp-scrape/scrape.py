# -*- coding: utf-8 -*-
"""
All constants/globals (e.g., CUISINES list, RATING_CUTOFF, SEARCH_LIMIT, etc.)
are located in settings.py and can be modified there.
"""

from __future__ import print_function
from settings import *  # has all globals
from urllib.error import HTTPError
import json
import requests
import sys


def write_to_json(dic):
    # Prepend all files with "bid-" so we don't have filenames starting with weird characters
    filename = "./data/bid-" + dic["BusinessId"] + ".json"
    with open(filename, 'w') as f:
        json.dump(dic, f, indent=2)


def open_memo(filename):
    with open(filename, 'w+') as f: # technically just reading, but need to create if it doesn't yet exist
        memo = f.read().splitlines()
        return memo


def append_to_memo(item_to_append):
    with open("memo.txt", "a") as f:
        f.write(item_to_append + "\n")


def build_item_dic(biz, cuisine):
    item = {"BusinessId": biz["id"], "Address": biz["location"]["display_address"][0], "Cuisine": cuisine,
            "Name": biz["name"], "NumReviews": biz["review_count"], "Rating": biz["rating"],
            "Zipcode": biz["location"]["zip_code"], "Latitude": biz["coordinates"]["latitude"],
            "Longitude": biz["coordinates"]["longitude"]}
    return item


def main():
    memo = open_memo("memo.txt") # the list of BusinessIds that we already uploaded
    headers = {'Authorization': 'Bearer %s' % API_KEY}

    try:
        for cuisine in cuisines:
            print("Processing %s cuisine:" % cuisine)
            current_offset = OFFSET # always starts at OFFSET but increments by SEARCH_LIMIT after every request
            params = {
                'categories': cuisine,
                'location': 'New York City',
                'offset': current_offset,
                'limit': SEARCH_LIMIT
            }
            r = requests.get(url=API_HOST + SEARCH_PATH, params=params, headers=headers)
            parsed = json.loads(r.text)

            total_num_businesses = parsed["total"]
            total_num_pages = total_num_businesses // SEARCH_LIMIT

            num_businesses_this_cuisine_stored = 0

            # Each i is a new request and page
            for i in range(1, total_num_pages + 1) :
                print("Processing page %d for cuisine %s\n" % (i, cuisine))

                if num_businesses_this_cuisine_stored >= MAX_BUSINESS_COUNT_PER_CUISINE:
                    break
                r = requests.get(url=API_HOST + SEARCH_PATH, params=params, headers=headers)
                parsed = json.loads(r.text)

                try:
                    for biz in parsed["businesses"]:

                        # if we already stored this business id, don't add it to the database
                        if biz["id"] in memo:
                            continue

                        # Check total_num_pages - 1 so that we don't have to deal with num records on last page
                        if ((i == total_num_pages - 1) or
                                (num_businesses_this_cuisine_stored >= MAX_BUSINESS_COUNT_PER_CUISINE)):
                            break

                        num_businesses_this_cuisine_stored += 1
                        item = build_item_dic(biz, cuisine)
                        write_to_json(item)  # append to the db json file
                        memo.append(item["BusinessId"])  # append to the list that's currently open
                        append_to_memo(item["BusinessId"])  # append to the memo (list of already processed bids) file

                    params['offset'] += SEARCH_LIMIT
                except Exception as err:
                    print(err)

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
