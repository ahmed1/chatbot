# Yelp scraping

## Overview
This program scrapes 5000+ Manhattan restaurants from Yelp using the Yelp API and uploads 
pertinent data about each restaurant to a DynamoDB table.

This assumes you have configured your AWS account to be accessed programmatically 
and that you have a DynamoDB table called "yelp-restaurants"



## 1. Install dependencies

To install the dependencies, run:   
`pip install -r requirements.txt`

## 2. Set Yelp API key
Create a file in this directory called *creds.txt* and paste your Yelp API key in it. 

## 3. Set scrape parameters
All parameters can be set in *settings.py*.

##### Pagination parameters
- **SEARCH_LIMIT**: the number of items to return per page
- **OFFSET**: the initial amount to offset on each iteration (will be incremented by SEARCH_LIMIT each iteration)
- **MAX_BUSINESS_COUNT_PER_CUISINE**: self-explanatory. Currently set to 1100 

##### Data category parameters
- **CITIES**: the list of cities to be searched
- **cuisines**: the list of cuisines within CITIES to be scraped. For simplicity, we use a subset of Yelp categories.

## 4. Execute the pipeline
Make the script executable if it is not already:  
`chmod +x run_pipeline.sh`  
Next, run it:  
`./run_pipeline.sh` 


## More about Yelp API
Please refer to [API
documentation](https://www.yelp.com/developers/documentation/v3)
for more details on how to use the API.
