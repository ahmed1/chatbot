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
    print("EVENTTT: ", event)

    data = event['Records'][0]['body']


    data = data.replace('\n', ' ')
    print('DATAAA: /{}/'.format(data), type(data))
    
    data = dict(eval(data))

    print('DATAAA: /{}/'.format(data), type(data))

    number_of_people = data['number_of_people']
    name = data['name']
    cuisine = data['cuisine']
    dining_time = data['dining_time']
    location = data['location']
    phone_number = data['phone_number']
    zip_code = data['zip_code']
    
    # hard-coded below for testing. delete when done
    #number_of_people = "3"
    #name = "ted"
    #cuisine = "pizza"
    #dining_time = "23:00"
    #location = "new york city"
    #phone_number = "3473563326"
    #zip_code = "10000"
    
    print('EVENTTTT: ', event)
    # sys.exit()
    # Put the user query into the query DSL for more accurate search results.
    # Note that certain fields are boosted (^).
    query = {
      "query": {
        "match": {
        #"match_all": {
          "Cuisine": cuisine
          #"Cuisine": 'pizza' 
          
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
    # Add the search results to the response
    r = r.json()
    
    #print(json.dumps(r))
    
    business_id = r['hits']['hits'][0]['_source']['RestaurantID']
    
    print('biz id is: {}'.format(business_id))
    
    # test biz id that we know is in the dynamo table
    #business_id = "04xHcYsqA3jCzpsX1Vs8ZQ"
   
    # query dynamodb
    client = boto3.client('dynamodb')
    response = client.get_item(TableName='yelp-restaurants', Key = {'BusinessId' : {'S': business_id }} )
    print("RESPONSEEE DYNAMO", response)

    recom_busin = response['Item']

    recom_name = recom_busin['Name']['S']
    recom_address = recom_busin['Address']['S']

    # final message for sns
    notification = "Hello {}! Here is my {} restaurant suggestions for {} people, for today at {}: 1. {}, located at {}.".format(name.capitalize(), 
    cuisine.capitalize(), number_of_people, dining_time, recom_name, recom_address)
    

    # invoke SNS
    client = boto3.client('sns')
    client.publish(PhoneNumber='+1' + phone_number, Message = notification)

    return r
