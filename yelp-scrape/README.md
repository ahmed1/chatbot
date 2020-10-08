# Yelp scraping

## Overview
This program scrapes 5000+ Manhattan restaurants from Yelp using the Yelp API.

Requirements:  
- 5000+  
- Manhattan  
- Get restaurants by self-defined cuisine types (by adding cuisine type in
  search term such as "chinese restaurants")  
- Each cuisine type should have around 1000 restaurants 
- Make sure restaurants are not duplicated  

Please refer to [API
documentation](https://www.yelp.com/developers/documentation/v3)
for more details on how to use the API.

## Steps to run

First, create a virtual environment in the root folder of this project:  
`python3 -m venv env`  
Next, activate the virtual environment by doing the following:  
`source env/bin/activate`   
Once activated, install the dependencies as described below. Once you are done
working with the project for the day, deactivate the virtual environment:
`deactivate`  

To install the dependencies, run:
`pip install -r requirements.txt`.

Categories are hardcoded.
Simply run the code without specifying any arguments:
`python yelp_scrape.py`



After populating db.json (in the correct format),
use the following to put a set of items from a json onto DynamoDB:
`aws dynamodb batch-write-item --request-items file://aws-requests.json`
