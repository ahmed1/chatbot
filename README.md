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
    - [CloudFront](#cloudfront)
    - [Yelp Scraping](#yelp-scraping)
    - [Front-end](#front-end)
    - [API Gateway](#api-gateway)
    - [Lambda functions (general setup)](#lambda-setup)
    - [Lambda LF0](#lambda-lf0)
    - [Lex](#lex)
    - [Lambda LF1](#lambda-lf1)
    - [SQS](#sqs)
    - [Lambda LF2](#lambda-lf2)
    - [CloudWatch](#cloudwatch)
    - [DynamoDB](#dynamodb)
    - [ElasticSearch](#elasticsearch)
    - [SNS](#sns)
    - [Cognito](#cognito)
    

## Demo
Below, a demo of a user registering for a new account and talking to the
chatbot.  
<img src="https://github.com/ashoukr/chatbot/blob/main/media/vid/demo.gif" width="100%" />

At the end of the process, the user receives a text message which looks like
this:  
<img src="https://github.com/ashoukr/chatbot/blob/main/media/img/text_message.jpg" width="60%"/>


## Architecture Overview

### Auto-Deployment
We used CodePipeline to auto-deploy code from our `master` branch on GitHub to S3. We also used the CloudFront content delivery network to distribute our
website and replicate the distribution configuration across multiple edge
locations around the world for caching content and providing fast delivery of
the website.  

Here is the flowchart for this process:  
<img src="https://github.com/ashoukr/chatbot/blob/main/media/img/chatbot-codepipeline.png" />

### Full Architecture Diagram
Here is the flowchart of our full architecture diagram.  
<img src="https://github.com/ashoukr/chatbot/blob/main/media/img/architecture-diagram.png" width="100%"/>


## Individual Components

### S3
Ahmed

### CodePipeline
The front-end is hosted in an S3 bucket. Since editing those files directly is impossible and downloading, editing, then reuploading is clumsy and inefficient, we decided to use CodePipeline. Whenever we push to our `master` branch in our GitHub repository, CodePipeline will pull those changes, then clone them to our S3 bucket. This makes for easy integration between GitHub and S3.

### CloudFront
The website source files are hosted on S3, but we also use a CDN called CloudFront to replicate configurations of the distribution to edge locations around the world, for caching content and providing fast delivery of the website.  

### Yelp Scraping
We wrote a series of python scripts (and one `run_pipeline.sh` script, which executes all python scripts). The python scripts scrape restaurant data from Yelp using the Yelp Fusion API, then store a subset of this data in DynamoDB and our Elasticsearch index. More information about Yelp Scraping can be found here:
[https://github.com/ashoukr/chatbot/blob/main/yelp-scrape/README.md](https://github.com/ashoukr/chatbot/blob/main/yelp-scrape/README.md)

### Front-end
We used starter code from [https://github.com/ndrppnc/cloud-hw1-starter](https://github.com/ndrppnc/cloud-hw1-starter) and did not change it much, since front-end development was not an important part of this project for us. The main thing we did was replace the sdk (`apigClient.js`) with the one we generated in API Gateway. We also added `userprofile.js` and `verifier.js`, both for the purpose of authenticating the user via Cognito.
 
### API Gateway
* We used the swagger API provided.
* We used the `Enable Cores` in the UI to add proper headers for POST method to work properly.
* However this did not add all the proper headers so we added them manually.
    * In the `Method Response` under `OPTIONS` and `POST`, we added the following response headers for 200 response:
        * `Access-Control-Allow-Headers`, `Access-Control-Allow-Origin`, `Access-Control-Allow-Credentials`, `Access-Control-Allow-Methods`
    * In the `Integration Response` under `OPTIONS` and `POST`, we added the following header mappings corresponding to the above mappings in order: 
        * 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token', '*', 'true', 'POST'

### General Lambda Setup
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

#### Main Intents
* DiningSuggestionsIntent
    * You can ask questions like "Can you help me find a restaurant" or you can give a statement like "I want to go eat with friends" or "I am hungry" which will trigger this intent.
    * Intent requires 8 different slots: `cusine`, `name`, `location`, `zip_code`, `dining_time`, `date`, `number_of_people`, and `phone_number`. 
        * In addition to these questions, we trained a number of corresponding utternaces it can use to extract matching information
        * There are a maximum of 2 retries before the question is skipped.

* GreetingIntent
    * You can ask questions like "What's up" or add statements like "Hey" or "Hello" to trigger this intent
    * Intent requires 1 slot: `name`
        * Multiple corresponding utterances given to extract name from user input
        * There are a miximum of 2 retries before the question is skipped.
* ThankYouIntent
    * Once a user says an utterance like "Thank you bot", "Thank you", etc. this intent is triggered
    * No slots required here


#### Code Fullfillment
This is done by setting LF1 as an initialization and validation code hook in Lex, and using `elicit_slot` in LF0 whenever a slot input is invalid. See The next section for more info.
    
### Lambda LF1
In a nutshell, LF1 takes events from Lex, validates them, then enqueues the message to SQS. 

The event is first parsed to see which intent sent it. If it's the ThankYouIntent or the GreetingIntent, LF1 will simply build a response of the following form and send it back:
```
# sample response for ThankYouIntent
res = {
    "sessionAttributes": {},
    "dialogAction": {
        "type": "Close",
        "fulfillmentState": "Fulfilled",
        "message" : {
            "contentType" : "PlainText",
            "content" : "No problem!"
        }
    }
}    
return res
```
This is the end of LF1's involvement with the ThankYouIntent and GreetingIntent.

On the other hand, if the intent value is DiningSuggestionsIntent, we do some validation throughout the conversation. The validation is a little tricky in that we have designed it to validate after each user input (mid-conversation). We feel that this is the better than validating at the conversation so that the user does not have to retype their whole list of preferences. This is done by setting LF1 as an initialization and validation code hook in Lex, and using `elicit_slot` in LF0 whenever a slot input is invalid. 

These are the intents LF1 validates:
- Number of people : must be greater than 0 and less than 20
- Phone number: must be 9 digits
- Date: day should be either current day/any day after the current day
- Time: greater than the current time if date is today
- Cuisine: must be one of the 5 cuisine types (non case-sensitive): ['indian', 'italian', 'burgers','chinese', 'pizza'])

If any of these are invalid, the chatbot will call `elicit_slot` to tell the user that the input is invalid and ask for another input.

Once all slots are collected and validated, the message is enqueued to SQS, and a return message is sent to the user, saying that the bot will look in its directory and send them a text message in a moment with restaurant suggestions.

### SQS
Ahmed

### Lambda LF2

* CloudWatch Trigger is explained below

* Once the data is obtained from SQS, we then parse it to grab all necessary fields.
* We used the AWS4Auth to make a request to elastic search

```python=

region = 'us-east-1' # For example, us-west-1
service = 'es'
credentials = boto3.Session().get_credentials()
awsauth = AWS4Auth(credentials.access_key, credentials.secret_key, region, service, session_token=credentials.token)

```
* Then we set up query using the cuisine provided by user 

```python=
query = {
  "query": {
    "match": {
      "Cuisine": cuisine
    }
  }
} 
headers = { "Content-Type": "application/json" }
# make query and get 3 different restaurants
r = requests.get(url, auth=awsauth, headers=headers, data=json.dumps(query))
```

* Used the RestaurantID 

### CloudWatch
We created a CloudWatch rule which triggers LF2 once every minute. While we could have simply added a SQS trigger to LF2, we used a CloudWatch rule to have more control over polling intervals. Thus, LF2 attempts to dequeue the next item from SQS. If such an item exists (i.e. if the queue is not empty) then LF2 will get data from the ES index and the DynamoDB table, then make a recommendation to the user as a string. It will then send this string to SNS.

### DynamoDB
We simply used the AWS web console to create a table. The `upload_to_dynamodb.py` script takes care of populating it with Yelp data.

We populated the table by simply iterating over the list of restaurants we scraped and doing the following
```
restaurant["insertedAtTimestamp"] = str(datetime.datetime.now())
table.put_item(Item=restaurant)
```
, where `restaurant` is the current restaurant in the iteration and `table` is the table we're inserting into.

See below for more info:  
[https://github.com/ashoukr/chatbot/blob/main/yelp-scrape/README.md](https://github.com/ashoukr/chatbot/blob/main/yelp-scrape/README.md)

### ElasticSearch
Ahmed: Setup


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

We populated the index by simply iterating over the list of restaurants we scraped and doing an `es.index(index=path, doc_type="_doc", id=str(index), body=doc)`, where `index` is the `i`th iteration and `doc` is the key:value object taking the form: 
```
doc = {
    "Cuisine": restaurant["Cuisine"],
    "RestaurantID": restaurant["BusinessId"]
}
```
More info can be seen here, or by viewing the `upload_to_elastic_search.py` file: 
[https://github.com/ashoukr/chatbot/blob/main/yelp-scrape/README.md](https://github.com/ashoukr/chatbot/blob/main/yelp-scrape/README.md)

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
As a fun add-on, we decided to add authentication. We created a userpool, and a new client app within that pool. Since the callback URL (where to redirect to once the user is signed in) must use https (not http), we used our CloudFront URL. We used an authorization code grant flow whereby the user receives a code via email upon registration and must enter the code on the screen to activate their account.

Cognito has some nice built-in forms to handle registration and login. This is convenient in that we did not have to create a separate web page just for the form. We used one of these, as shown below:  
<img src="https://github.com/ashoukr/chatbot/blob/main/media/img/cognito.png" />
