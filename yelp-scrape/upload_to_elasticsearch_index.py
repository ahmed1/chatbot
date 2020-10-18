from elasticsearch import Elasticsearch, RequestsHttpConnection
from requests_aws4auth import AWS4Auth
from decimal import Decimal
import boto3
import json

host = 'search-yelp-restaurants-lg4z52z76iaf3lkg54o2jdcj2a.us-east-1.es.amazonaws.com'
path = 'restaurants' # the Elasticsearch API endpoint
region = 'us-east-1' # For example, us-west-1

service = 'es'
credentials = boto3.Session().get_credentials()
awsauth = AWS4Auth(credentials.access_key, credentials.secret_key, region, service, session_token=credentials.token)

es = Elasticsearch(
    hosts=[{'host': host, 'port': 443}],
    http_auth=awsauth,
    use_ssl=True,
    verify_certs=True,
    connection_class=RequestsHttpConnection
)

#es.index(index=path, doc_type="_doc", id="1", body=document)
#print(es.get(index=path, doc_type="_doc", id="1"))


def upload_restaurants_to_es_index(restaurants):
    index = 1
    for restaurant in restaurants:
        #if index >= 2:
        #    break
        doc = {
            "Cuisine": restaurant["Cuisine"],
            "RestaurantID": restaurant["BusinessId"],
        }
        es.index(index=path, doc_type="_doc", id=str(index), body=doc)
        #es.delete(index=path, doc_type="_doc", id=str(index))
        index += 1


def main():
    with open("data/db/db.json") as json_file:
        restaurant_list = json.load(json_file, parse_float=Decimal)
    upload_restaurants_to_es_index(restaurant_list)


if __name__ == '__main__':
    main()

