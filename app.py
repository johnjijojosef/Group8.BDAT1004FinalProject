from flask import Flask, jsonify, request, render_template
import pymongo
from pymongo.mongo_client import MongoClient
from pymongo import MongoClient
import json
import urllib.parse

app = Flask(__name__)

# Specify route for index.html - Home Page
@app.route('/')
def index():
	return render_template('index.html') 


@app.route('/google-charts/bar-chart')
def google_bar_chart():

    # Connecting to cloud database (MongoDb)
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

    # Perform aggregation to group by Business Name and SentimentLabel and calculate count
    pipeline = [
        {
            "$match": {
                "SentimentLabel": "positive"
            }
        },
        {
            "$group": {
                "_id": {
                    "BusinessName": "$Business Name"
                    #,                "SentimentLabel": "$SentimentLabel"
                },
                "Count": {"$sum": 1}
            }
        },
        {
            "$project": {
                "_id": 0,
                "BusinessName": "$_id.BusinessName",
                "SentimentLabel": "$_id.SentimentLabel",
                "Count": 1
            }
        },
        {
            "$sort": {
                "Count": -1
            }
        }
    ]

    aggregated_data = list(collection.aggregate(pipeline))
    #print(aggregated_data)

    custom_data = {'Business Name' : 'Count'}
    for x in aggregated_data:
        custom_data[x['BusinessName']] = (x['Count'])

    # Sending request to the template 'time-series.html' along with the custom data
    return render_template('bar-chart.html', data=custom_data)


# Generic route for each product request
@app.route('/google-charts/<restaurant>')
def google_time_series(restaurant):

    # Connecting to cloud database (MongoDb)
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

    # Perform aggregation to group by Business Name and SentimentLabel and calculate count
    pipeline = [
        {
            "$match": {
                "SentimentLabel": {"$in": ["positive", "negative"]},
                "Business Name": restaurant
            }
        },
        {
            "$group": {
                "_id": {
                    #"BusinessName": "$Business Name",
                    "SentimentLabel": "$SentimentLabel"
                },
                "Count": {"$sum": 1}
            }
        },
        {
            "$project": {
                "_id": 0,
                "BusinessName": "$_id.BusinessName",
                "SentimentLabel": "$_id.SentimentLabel",
                "Count": 1
            }
        },
        {
            "$sort": {
                "BusinessName": 1,
                "SentimentLabel": -1
            }
        }
    ]

    aggregated_data = list(collection.aggregate(pipeline))
    #print(aggregated_data)

    custom_data = {'SentimentLabel' : 'Count'}
    for x in aggregated_data:
        custom_data[x['SentimentLabel']] = (x['Count'])

    pipelinetable = [
        {
            "$match": {
                "SentimentLabel": {"$in": ["positive", "negative"]},
                "Business Name": restaurant
            }
        },
        {
            "$sort": {
                "SentimentLabel": -1,
                "SentimentScore": -1
            }
        },
        {
            "$project": {
                "_id": 0,
                "SentimentLabel": "$SentimentLabel",
                "Review": 1
            }
        },
        {
            "$limit": 35
        }
    ]

    aggregated_tabledata = list(collection.aggregate(pipelinetable))
    #print(aggregated_tabledata)

    custom_tabledata = {'Reviews' : 'Review Type'}
    for x in aggregated_tabledata:
        custom_tabledata[x['Review']] = (x['SentimentLabel'])

    # Sending request to the template 'time-series.html' along with the custom data
    return render_template('detail-pie-table-chart.html', data=custom_data, tableData=custom_tabledata, title=restaurant)

if __name__ == "__main__":
    app.run()