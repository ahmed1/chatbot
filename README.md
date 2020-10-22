# Dining Concierge Chatbot
Built by Theodore Hadges and Ahmed Shoukr


## 1. Architecture
We used CodePipeline to auto-deploy code from our `master` branch on GitHub to
S3. We also used the CloudFront content delivery network to distribute our
website and replicate the distribution configuration across multiple edge
locations around the world for caching content and providing fast delivery of
the website. Here is the flowchart for this process:
<img src="https://github.com/ashoukr/chatbot/blob/main/media/img/chatbot-codepipeline.png" />
<hr>
Here is the flowchart of our full architecture diagram.
<img src="https://github.com/ashoukr/chatbot/blob/main/media/img/architecture-diagram.png" width="100%"/>
