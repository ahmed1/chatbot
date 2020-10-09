import boto3
import json
import requests
from requests_aws4auth import AWS4Auth
import sys
region = 'us-east-1' # For example, us-west-1
service = 'es'
credentials = boto3.Session().get_credentials()
awsauth = AWS4Auth(credentials.access_key, credentials.secret_key, region, service, session_token=credentials.token)

host = 'search-yelp-restaurants-lg4z52z76iaf3lkg54o2jdcj2a.us-east-1.es.amazonaws.com' # For example, search-mydomain-id.us-west-1.es.amazonaws.com
index = 'restaurants'
url = 'https://' + host + '/' + index + '/' + '_search'

# Lambda execution starts here
def lambda_handler(event, context):

    data = event['body']
    
    number_of_people = data['number_of_people']
    name = data['name']
    cuisine = data['cuisine']
    dining_time = data['dining_time']
    location = data['location']
    phone_number = data['phone_number']
    zip_code = data['zip_code']

    print('EVENTTTT: ', event)
    # sys.exit()
    # Put the user query into the query DSL for more accurate search results.
    # Note that certain fields are boosted (^).
    query = {
      "query": {
        "match": {
          "Cuisine": cuisine
        }
      }
    } 

    # ES 6.x requires an explicit Content-Type header
    headers = { "Content-Type": "application/json" }

    # Make the signed HTTP request
    r = requests.get(url, auth=awsauth, headers=headers, data=json.dumps(query))

    # Create the response and add some extra content to support CORS
    response = {
        "statusCode": 200,
        "headers": {
            "Access-Control-Allow-Origin": '*'
        },
        "isBase64Encoded": False
    }
    print(r)
    # Add the search results to the response
    r = r.json()
    
    business_id = r['hits']['hits'][0]['_source']['RestaurantID']
    
    
    # query dynamodb
    client = boto3.client('dynamodb')
    response = client.get_item(TableName='yelp-restaurants', Key = {'BusinessId' : {'S': business_id }} )
    print("RESPONSEEE DYNAMO", response)

    recom_busin = response['item']

    recom_name = recom_busin['Name']['S']
    recom_address = recom_busin['Address']['S']

    # final message for sns
    notification = "Hello! Here is my {} restaurant \
        suggestions for {} people, for today at {}: 1. \
        {}, located at {}.".format(cuisine.capitalize(), number_of_people,
        dining_time, recom_name, recom_address)
    

    # invoke SNS
    client = boto3.client('sns')
    
    return r