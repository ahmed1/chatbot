import json

# import requests
import boto3
import sys


def get_dining_details(slots):

    number_of_people = slots['number_of_people']
    name = slots['name']
    cuisine = slots['cuisine']
    dining_time = slots['dining_time']
    location = slots['location']
    phone_number = slots['phone_number']
    zip_code = slots['zip_code']



def lambda_handler(event, context):
    """

    """

    client = boto3.client('sqs')



    cur_intent = event['currentIntent']['name']
    if cur_intent == 'DiningSuggestionsIntent':
        slots = event['currentIntent']['slots']
        # dining_details = get_dining_details(slots)
    else:
        print('SOMETHING IS BROKEN')
        sys.exit()
    


    # call sqs

    queue_url = 'https://sqs.us-east-1.amazonaws.com/922059106485/chatbot-queue'
    message = json.dumps(slots)
    print(message)
    response = client.send_message(QueueUrl = queue_url, MessageBody=message)


    print("RESPONSE FROM LEFT SIDE SQS", response)






    # print('EVENTTT', event)

    # return {
    #     "statusCode": 200,
    #     "body": json.dumps({
    #         "message": "hello world",
    #         # "location": ip.text.replace("\n", "")
    #     }),
    # }
    return "I will look in my directory for a place that matches your needs and get back to you shortly via SMS with a recommendation."
