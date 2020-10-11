# Uncomment the two lines below to clear cache of already processed business IDs
rm memo.txt
rm ./data/bid*

python3 scrape.py # scrape and write each biz to a json in ./data
python3 compile_data.py # make a master db file in ./data/db called db.json
python3 upload_to_dynamodb.py # upload the contents from ./data/db/db.json
