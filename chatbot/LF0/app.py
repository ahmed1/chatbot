import json
import boto3
# import requests


def lambda_handler(event, context):
    
    message = event['messages'][0]['unstructured']['text']
    print('MESSAGE LOGGED: ', message)
    # send message to Lex
    client = boto3.client('lex-runtime')
    response = client.post_text(botName='ConceirgeBot', botAlias = 'ConceirgeBot', userId='string', 
                inputText = message)
    print('RESPONSE::: ', response)
    res = response['message']
    print('MESSSAGE::::', res)
    """Sample pure Lambda function

    Parameters
    ----------
    event: dict, required
        API Gateway Lambda Proxy Input Format

        Event doc: https://docs.aws.amazon.com/apigateway/latest/developerguide/set-up-lambda-proxy-integrations.html#api-gateway-simple-proxy-for-lambda-input-format

    context: object, required
        Lambda Context runtime methods and attributes

        Context doc: https://docs.aws.amazon.com/lambda/latest/dg/python-context-object.html

    Returns
    ------
    API Gateway Lambda Proxy Output Format: dict

        Return doc: https://docs.aws.amazon.com/apigateway/latest/developerguide/set-up-lambda-proxy-integrations.html
    """

    # try:
    #     ip = requests.get("http://checkip.amazonaws.com/")
    # except requests.RequestException as e:
    #     # Send some context about this error to Lambda Logs
    #     print(e)

    #     raise e
    # msg = "Hey, What's up dude. I’m still under development. Please come back later."
    return {
        "statusCode": 200,
        'headers': {
            'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'OPTIONS,POST'
        },
        "body": str(res)
    }
