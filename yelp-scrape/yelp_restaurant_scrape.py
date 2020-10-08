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

def main():
    # before this, must run
    # db = read_from_json() # dict is copy of db
    headers = {'Authorization': 'Bearer %s' % API_KEY}

    try:
        for cuisine in cuisines:
            current_offset = OFFSET # always starts at OFFSET but increments by SEARCH_LIMIT after every request
            PARAMS = {'categories': cuisine, 'location': 'New York City', 'offset': current_offset, 'limit': SEARCH_LIMIT}
            r = requests.get(url=API_HOST + SEARCH_PATH, params=PARAMS, headers=headers)
            parsed = json.loads(r.text)

            total_num_businesses = parsed["total"]
            total_num_pages = total_num_businesses // SEARCH_LIMIT

            num_businesses_this_cuisine_stored = 0

            # Each i is a new request and page
            for i in range(0, total_num_pages):
                if num_businesses_this_cuisine_stored >= MAX_BUSINESS_COUNT_PER_CUISINE:
                    break
                PARAMS = {'categories': cuisine, 'location': 'New York City', 'offset': current_offset, 'limit': SEARCH_LIMIT}
                r = requests.get(url=API_HOST + SEARCH_PATH, params=PARAMS, headers=headers)
                parsed = json.loads(r.text)

                # Check total_num_pages - 1 so that we don't have to deal with num records on last page
                for biz in parsed["businesses"]:
                    if ((i == total_num_pages - 1) or \
                            (num_businesses_this_cuisine_stored >= MAX_BUSINESS_COUNT_PER_CUISINE)):
                        break
                    num_businesses_this_cuisine_stored += 1
                    print("Current restaurant: %s " % biz["name"])
                current_offset += SEARCH_LIMIT

    # Once we figure out schema, do something like this:
    # write_to_json(restaurants)

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
