import boto3
import json
import requests
from requests_aws4auth import AWS4Auth
import sys
from datetime import datetime
region = 'us-east-1' # For example, us-west-1
service = 'es'
credentials = boto3.Session().get_credentials()
awsauth = AWS4Auth(credentials.access_key, credentials.secret_key, region, service, session_token=credentials.token)

# Create sqs client
sqs = boto3.client('sqs')
queue_url = 'https://sqs.us-east-1.amazonaws.com/922059106485/chatbot-queue'

host = 'search-yelp-restaurants-lg4z52z76iaf3lkg54o2jdcj2a.us-east-1.es.amazonaws.com' # For example, search-mydomain-id.us-west-1.es.amazonaws.com
index = 'restaurants'
url = 'https://' + host + '/' + index + '/' + '_search'

# Lambda execution starts here
def lambda_handler(event, context):
  
    try:
      
      # Receive message from SQS queue
      response = sqs.receive_message(
      QueueUrl=queue_url,
      AttributeNames=[
          'SentTimestamp'
      ],
      MaxNumberOfMessages=1,
      MessageAttributeNames=[
          'All'
      ],
      VisibilityTimeout=0,
      WaitTimeSeconds=0
      )
  
      message = response['Messages'][0]
      receipt_handle = message['ReceiptHandle']
      
      # Delete received message from queue
      sqs.delete_message(
          QueueUrl=queue_url,
          ReceiptHandle=receipt_handle
      )
      print('Received and deleted message: %s' % message)
      
      data = message['Body']
      
      # Commented out since we're polling rather than using trigger
      #data = event['Records'][0]['body']
      
      data = data.replace('\n', ' ')
      data = dict(eval(data))
      
  
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
      
      business_ids = []
      for i in range (0,3):
        business_ids.append(r['hits']['hits'][i]['_source']['RestaurantID'])
     
      notification = "Hello {}! Here are my {} restaurant suggestions for {} people, for today at {}:\n".format(
        name.capitalize(), 
        cuisine.capitalize(), 
        number_of_people, 
        datetime.strptime(dining_time, "%H:%M").strftime("%I:%M %p")) # display as AM/PM (not 24 hour)
      
      # query dynamodb
      client = boto3.client('dynamodb')
      for i in range(0,3): # get info for the 3 businesses in business_ids
        res = client.get_item(TableName='yelp-restaurants', Key = {'BusinessId' : {'S': business_ids[i] }} )
        recom_name = res['Item']['Name']['S']
        recom_address = res['Item']['Address']['S']
        notification += "\n{}. {}, located at {}.".format(i+1, recom_name, recom_address)
        
      notification += "\n\nEnjoy your meal!"
  
      # invoke SNS
      client = boto3.client('sns')
      client.publish(PhoneNumber='+1' + phone_number, Message = notification)
  
      return
      #return r
    except:
      print("queue empty")
