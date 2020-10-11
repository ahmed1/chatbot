from decimal import Decimal
import json
import boto3

def load_restaurants(restaurants, dynamodb=None):
    if not dynamodb:
        dynamodb = boto3.resource('dynamodb', region_name='us-east-1')

    table = dynamodb.Table('yelp-restaurants')
    for restaurant in restaurants:
        table.put_item(Item=restaurant)

if __name__ == '__main__':
    
    with open("data/db/db.json") as json_file:
        restaurant_list = json.load(json_file, parse_float=Decimal)
    load_restaurants(restaurant_list)

