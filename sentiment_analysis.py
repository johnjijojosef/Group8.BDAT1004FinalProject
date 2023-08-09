import pymongo
import urllib.parse
import pandas as pd
import numpy as np
from scipy.special import softmax
from transformers import AutoModelForSequenceClassification, AutoTokenizer

# Load sentiment analysis model and tokenizer
MODEL = "cardiffnlp/twitter-roberta-base-sentiment-latest"
model = AutoModelForSequenceClassification.from_pretrained(MODEL)
tokenizer = AutoTokenizer.from_pretrained(MODEL)

username = 'dbuser'
password = 'Pa$$word@61803'
escaped_username = urllib.parse.quote_plus(username)
escaped_password = urllib.parse.quote_plus(password)
database_url = 'dbcluster1.2v8vfcl.mongodb.net'
db_name = 'Database1'

# Create the MongoDB connection URI with the escaped username and password
uri = f"mongodb+srv://{escaped_username}:{escaped_password}@{database_url}/{db_name}"

# Connect to your MongoDB using the URI
client = pymongo.MongoClient(uri)
    
# Connect to the MongoDB database
db = client["Database1"]
collection = db["Collection1"]

reviews = collection.find({}, {"Business Name": 1, "Review": 1, "_id": 1}).limit(100)

while reviews.alive:
    
    for document in reviews: #collection.find():
        #print(document)
        result = {}
        business_name = document.get("Business Name", "N/A")
        review = document.get("Review", "N/A")
        Id = document.get("_id", "N/A")

        text = review
        encoded_input = tokenizer(text, return_tensors='pt')
        output = model(**encoded_input)

        #scores = output[0][0].detach().numpy()
        #scores = softmax(scores)


        scores = output.logits.detach().numpy()
        scores = softmax(scores, axis=1)
        sentiment_label = ["negative", "neutral", "positive"][np.argmax(scores)]
        sentiment_score = float(np.max(scores))
        print(sentiment_label, sentiment_score)

        # Update the collection with sentiment analysis results
        collection.update_one({"_id": Id}, {"$set": {"SentimentLabel": sentiment_label, "SentimentScore": sentiment_score}})
        #print()
    
    # Close the cursor and open a new one to prevent timeout
    reviews.close()
    reviews = collection.find({"_id": {"$gt": Id}}, {"Business Name": 1, "Review": 1, "_id": 1}).limit(100)
    reviews.close()
    
client.close()
