# Dining Concierge Chatbot

Teammates: [Theodore Hadges](https://github.com/theodorehadges) and [Ahmed Shoukr](https://github.com/ashoukr)

This is a chatbot which uses AWS services to ask a user questions and use their preferences to suggest a list of restaurants they may enjoy. 

The architecture is admittedly overkill for this application (it uses 11 different AWS services) but we wanted to use this project to practice and learn how to build a scalable cloud application.

## Table of Contents
1. [Demo](#demo)
    - [Demo](#demo)
2. [Architecture Overview](#architecture-overview)
    - [Auto-Deployment](#auto-deployment)
    - [Full Architecture Diagram](#architecture-diagram)
3. [Indvidual Components](#individual-components)
    - [S3](#s3)
    - [Yelp Scraping](#yelp-scraping)
    - [Front-end](#front-end)
    - [API Gateway](#api-gateway)
    - [Lambda functions (general setup)](#lambda-setup)
    - [Lambda LF0](#lambda-lf0)
    - [Lex](#lex)
    - [Lambda LF1](#lambda-lf1)
    - [SQS](#sqs)
    - [Lambda LF2](#lambda-lf2)
    - [DynamoDB](#dynamodb)
    - [ElasticSearch](#elasticsearch)
    - [SNS](#sns)
    - [Cognito](#cognito)
    

## Demo
Insert gif of working chatbot here

## Architecture Overview

### Auto-Deployment
We used CodePipeline to auto-deploy code from our `master` branch on GitHub to S3. We also used the CloudFront content delivery network to distribute our
website and replicate the distribution configuration across multiple edge
locations around the world for caching content and providing fast delivery of
the website. Here is the flowchart for this process:
<img src="https://github.com/ashoukr/chatbot/blob/main/media/img/chatbot-codepipeline.png" />

### Full Architecture Diagram
Here is the flowchart of our full architecture diagram.
<img src="https://github.com/ashoukr/chatbot/blob/main/media/img/architecture-diagram.png" width="100%"/>


## Individual Components

### S3
Ahmed

### Yelp Scraping
Ted
### Front-end
Ted
### API Gateway
Ahmed
### Lambda Setup
* We used the Serverless Application Model (SAM) CLI provided by Amazon to write all the lambda functions and test them locally.
* Additionally, this allowed us to manipulate all the infrastructure for the lambda functions.

```yaml
# sample template for LF0
Resources:
  LF0Function:
    Type: AWS::Serverless::Function 
    Properties:
      CodeUri: ./LF0/
      Handler: app.lambda_handler
      Runtime: python3.7
      Timeout: 200
      Events:
        LF0:
          Type: Api 
          Properties:
            Path: /LF0
            Method: get
```

* We used Docker to dockerize and send all 3 lambda functions to s3 before they were deployed using cloudformation to obtain full memory capacity for additional packages we may need.

* Each Lambda function has a requirements.txt file with additional packages we used such as `requests_aws4auth` used by LF2
* We also wrote a deployment script to automate this process

```shell
# deploy.sh
sam build --use-container
sam package --s3-bucket chatbot-cloudformation-template --output-template-file packaged.yaml
sam deploy --template-file ./packaged.yaml --stack-name chatbot-message-handler --capabilities CAPABILITY_IAM CAPABILITY_NAMED_IAM CAPABILITY_AUTO_EXPAND

```
### Lambda LF0
* Set up with API Gateway to receive user message and send it to Lex
* Given API Gateway necessary additional role to pass messages to this lambda
* Uses boto3 SDK to pass message to Lex

```python
client = boto3.client('lex-runtime')
response = client.post_text(botName='ConceirgeBot', botAlias = 'ConceirgeBot', userId='string', inputText = message)
```

* Returns body response to UI
### Lex
Ahmed
* Trained with multiple Intents -- discuss more 
### Lambda LF1
Ted
### SQS
Ahmed
### Lambda LF2
Ahmed
* What do we need to do for the cloudwatch trigger?
* 
### DynamoDB
Ted (setup and population)
### ElasticSearch
Ahmed: Setup
Ted: populate index

1. Used Development and testing domain type

2. We used `t3.small.elasticsearch` instance type with 1 node  for cost purposes. Because of this, we had to specify a policy presented by AWS to be able to create the cluster, then went back later and changed it to allow any AWS service to access the resource.
3. There are also no dedicated master nodes
4. No VPC used

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "AWS": "*"
      },
      "Action": "es:*",
      "Resource": "arn:aws:es:us-east-1:922059106485:domain/yelp-restaurants/*"
    }
  ]
}
```



```shell
# Sample PUT requrest used to insert data into elasticsearch for initial testing
# also creates index
$ http PUT https://search-yelp-restaurants-lg4z52z76iaf3lkg54o2jdcj2a.us-east-1.es.amazonaws.com/restaurants/Restaurant/6 Cuisine="chinese" RestaurantID="0CjK3esfpFcxIopebzjFxA"

{
    "_id": "4",
    "_index": "restaurants",
    "_primary_term": 1,
    "_seq_no": 0,
    "_shards": {
        "failed": 0,
        "successful": 1,
        "total": 2
    },
    "_type": "Restaurant",
    "_version": 1,
    "result": "created"
}

# Sample GET request used to ensure data inserted in elastic search
$ http GET https://search-yelp-restaurants-lg4z52z76iaf3lkg54o2jdcj2a.us-east-1.es.amazonaws.com/restaurants/Restaurant/1

# Delete restaurants table after testing
http DELETE https://search-yelp-restaurants-lg4z52z76iaf3lkg54o2jdcj2a.us-east-1.es.amazonaws.com/restaurants

```

* In Elastic Kibana, we used SQL WorkBench to query the tables created and ensure data was present in the elastic search cluster

```sql
show tables like %;
describe tables like %;
SELECT * FROM restaurants
```

* Finally, we gave LF2 Lambda a new role that allowed it to interact with the Elastic Search Cluster.

### SNS
Ahmed
* Here we created a basic topic called chatbot-sms without any additional configuration (none that I can remember)
* We added a new role to LF2 that allows it to communicate with this SNS topic.
* We used boto3 SDK provided to push sns requests to this service. This instantly sends a message to the user with all the details.

```python
client = boto3.client('sns')
client.publish(PhoneNumber = '+1' + phone_number, Message = notification)
```
### Cognito
Ted
