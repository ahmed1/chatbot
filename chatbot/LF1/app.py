import json

# import requests
import boto3
import sys
import time
import datetime
import os
import dateutil.parser
import logging

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)


# --- Helpers that build all of the responses ---


def elicit_slot(session_attributes, intent_name, slots, slot_to_elicit, message):
    return {
        'sessionAttributes': session_attributes,
        'dialogAction': {
            'type': 'ElicitSlot',
            'intentName': intent_name,
            'slots': slots,
            'slotToElicit': slot_to_elicit,
            'message': message
        }
    }


def delegate(session_attributes, slots):
    return {
        'sessionAttributes': session_attributes,
        'dialogAction': {
            'type': 'Delegate',
            'slots': slots
        }
    }


# --- Helper Functions ---


def build_validation_result(isvalid, violated_slot, message_content):
    return {
        'isValid': isvalid,
        'violatedSlot': violated_slot,
        'message': {'contentType': 'PlainText', 'content': message_content}
    }
    

def safe_int(n):
    """
    Safely convert n string value to int.
    Return -1 if the string is a decimal number or other.
    """
    if n is not None:
        try: # try to see if we can cast it to an int
            return int(n)
        except ValueError: # probably a decimal number inside of a string
            return -1
    return -1


def try_ex(func):
    """
    Call passed in function in try block. If KeyError is encountered return None.
    This function is intended to be used to safely access dictionary.

    Note that this function would have negative impact on performance.
    """

    try:
        return func()
    except KeyError:
        return None


def isvalid_cuisine(cuisine):
    valid_cuisines= ['chinese', 'italian', 'indian', 'pizza', 'burgers']
    #return cuisine.lower() in valid_cuisines
    return cuisine in valid_cuisines
    

def isvalid_num_people(number_of_people):
    return True if number_of_people > 0 and number_of_people < 20 else False


def isvalid_date(date_input):
    try:
        if datetime.datetime.strptime(date_input, '%Y-%m-%d').date() < datetime.date.today():
            return False
        return True
    except ValueError:
        return False
        

def isvalid_time(time_input, date_input):
    if datetime.datetime.strptime(date_input, '%Y-%m-%d').date() > datetime.date.today():
        return True
    if datetime.datetime.strptime(time_input, '%H:%M').time() < datetime.datetime.now().time():
        return False 
    return True


def validate_input(slots):
    cuisine = try_ex(lambda: slots['cuisine'])
    number_of_people = try_ex(lambda: slots['number_of_people'])
    date_input = try_ex(lambda: slots['date'])
    time_input = try_ex(lambda:slots['dining_time'])
    
    if date_input and not isvalid_date(date_input):
        return build_validation_result(
            False,
            'date',
            'Invalid date. Please enter a date that has not already passed.'
        )
    
    if time_input and date_input and not isvalid_time(time_input, date_input):
        return build_validation_result(
            False,
            'time_input',
            'You must select a time in the future.'
        )
        
    if number_of_people and not isvalid_num_people(safe_int(number_of_people)):
        return build_validation_result(
            False,
            'number_of_people',
            'Invalid number of people. Must be an integer of at least 1 and less than 20. How many people will there be?'
        )

    if cuisine and not isvalid_cuisine(cuisine):
        return build_validation_result(
            False,
            'cuisine',
            'We currently do not support {} as cuisine. We only support chinese, indian, italian, pizza, and burgers at this time. Please choose from one of these cuisines. What is your preferred cuisine?'.format(cuisine)
        )

    return {'isValid': True}
   
    
""" --- Functions that control the bot's behavior --- """


def DiningSuggestionsIntent(intent_request):
    
    """
    Performs dialog management and fulfillment for suggesting a dining cuisine.

    Beyond fulfillment, the implementation for this intent demonstrates the following:
    1) Use of elicitSlot in slot validation and re-prompting
    2) Use of sessionAttributes to pass information that can be used to guide conversation
    """
   
    location = try_ex(lambda: intent_request['currentIntent']['slots']['location'])
    dining_time = try_ex(lambda: intent_request['currentIntent']['slots']['dining_time'])
    date_input = try_ex(lambda: intent_request['currentIntent']['slots']['date'])
    cuisine = try_ex(lambda: intent_request['currentIntent']['slots']['cuisine'])
    number_of_people = try_ex(lambda: intent_request['currentIntent']['slots']['number_of_people'])
    name = try_ex(lambda: intent_request['currentIntent']['slots']['name'])
    phone_number = try_ex(lambda: intent_request['currentIntent']['slots']['phone_number'])
    zip_code = try_ex(lambda: intent_request['currentIntent']['slots']['zip_code'])
    
    session_attributes = intent_request['sessionAttributes'] if intent_request['sessionAttributes'] is not None else {}
    
    # Load suggestion history and track the current suggestion.
    suggestion = json.dumps({
         'location': location,
         'dining_time': dining_time,
         'date': date_input,
         'cuisine': cuisine,
         'number_of_people': number_of_people,
         'name': name,
         'phone_number': phone_number,
         'zip_code': zip_code
    })
    
    session_attributes['currentSuggestion'] = suggestion 

    if intent_request['invocationSource'] == 'DialogCodeHook':
        # Validate any slots which have been specified.  If any are invalid, re-elicit for their value
        validation_result = validate_input(intent_request['currentIntent']['slots'])
        if not validation_result['isValid']:
            slots = intent_request['currentIntent']['slots']
            slots[validation_result['violatedSlot']] = None

            return elicit_slot(
                session_attributes,
                intent_request['currentIntent']['name'],
                slots,
                validation_result['violatedSlot'],
                validation_result['message']
            )

        # Otherwise, let native DM rules determine how to elicit for slots and prompt for confirmation.  

        session_attributes['currentSuggestion'] = suggestion 
        return delegate(session_attributes, intent_request['currentIntent']['slots'])
        

    client = boto3.client('sqs')
    
    # call sqs
    slots = intent_request['currentIntent']['slots']

    queue_url = 'https://sqs.us-east-1.amazonaws.com/922059106485/chatbot-queue'
    message = json.dumps(slots) # should probably do a slots[slot_item].lower() on each slot item before sending
    response = client.send_message(QueueUrl = queue_url, MessageBody=message)

    ret = {
        "sessionAttributes": {},
        "dialogAction": {
            "type": "Close",
            "fulfillmentState": "Fulfilled",
            "message" : {
                "contentType" : "PlainText",
                "content" : "I will look in my directory for a place that matches your needs and get back to you shortly via SMS with a recommendation."
            }
        }
    }

    return ret
    

# --- Intents ---


def dispatch(intent_request):
    """
    Called when the user specifies an intent for this bot.
    """

    logger.debug('dispatch userId={}, intentName={}'.format(intent_request['userId'], intent_request['currentIntent']['name']))

    intent_name = intent_request['currentIntent']['name']

    # Dispatch to bot's intent handlers
    if intent_name == 'DiningSuggestionsIntent':
        return DiningSuggestionsIntent(intent_request)

    raise Exception('Intent with name ' + intent_name + ' not supported')
    

# --- Main handler ---


def lambda_handler(event, context):
    """
    Route the incoming request based on intent.
    The JSON body of the request is provided in the event slot.
    """
    # By default, treat the user request as coming from the America/New_York time zone.
    os.environ['TZ'] = 'America/New_York'
    time.tzset()
    logger.debug('event.bot.name={}'.format(event['bot']['name']))
    
    return dispatch(event)
