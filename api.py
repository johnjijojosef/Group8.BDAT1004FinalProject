from flask import Flask, render_template, jsonify
import pymongo
import requests
from bs4 import BeautifulSoup
import time
import urllib.parse
import uuid
import threading

app = Flask(__name__)

# MongoDB database configuration
username = 'dbuser'
password = 'Pa$$word@61803'
escaped_username = urllib.parse.quote_plus(username)
escaped_password = urllib.parse.quote_plus(password)
database_url = 'dbcluster1.2v8vfcl.mongodb.net'
db_name = 'Database1'

# Creating MongoDB connection
uri = f"mongodb+srv://{escaped_username}:{escaped_password}@{database_url}/{db_name}"

# Connect to MongoDB using the URI
client = pymongo.MongoClient(uri)
db = client[db_name]
collection = db['Collection1']

# Set user agent headers to mimic a web browser
headers = {
    'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/112.0'}

# Function to scrape reviews from a given URL
def get_reviews(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/112.0'}
    soup = BeautifulSoup(requests.get(url, headers=headers).content, 'html.parser')
    biz_id_element = soup.find('meta', attrs={"name": "yelp-biz-id"})
    if biz_id_element is None:
        return []

    biz_id = biz_id_element['content']
    review_url = "https://www.yelp.ie/biz/{biz_id}/review_feed?rl=en&q=&sort_by=relevance_desc&start={start}"
    reviews = []
    for start in range(0, 100, 5):
        r_url = review_url.format(biz_id=biz_id, start=start)
        data = requests.get(r_url, headers=headers).json()
        for r in data['reviews']:
            review_text = BeautifulSoup(r['comment']['text'], 'html.parser').text
            reviews.append(review_text)

    return reviews


# Function to process URLs, scrape reviews, and store them in the database
def process_urls():
    with open('url.txt', 'r') as url_file:
        urls = url_file.read().splitlines()

    for url in urls:
        business_name = BeautifulSoup(requests.get(url, headers=headers).content, 'html.parser').find('h1').text.strip()
        reviews = get_reviews(url)

        review_list = []
        for review in reviews:
            unique_id = str(uuid.uuid4())
            review_dict = {'ID': unique_id, 'Business Name': business_name, 'Review': review}
            review_list.append(review_dict)

        # Insert the reviews into the collection
        collection.insert_many(review_list)


@app.route('/')
def display_reviews():
    # Retrieve all reviews from the database
    reviews = list(collection.find({}, {'_id': 0}))

    return render_template('reviews.html', reviews=reviews)


@app.route('/api/all', methods=['GET'])
def get_all_items():
    reviews = list(collection.find({}, {'_id': 0}))
    return jsonify(reviews)


@app.route('/api/range/<int:start>/<int:end>', methods=['GET'])
def get_range_items(start, end):
    reviews = list(collection.find({}, {'_id': 0}))
    return jsonify(reviews[start:end])


@app.route('/api/item/<string:item_id>', methods=['GET'])
def get_item_by_id(item_id):
    review = collection.find_one({'ID': item_id}, {'_id': 0})
    return jsonify(review)


if __name__ == '__main__':
    # Run the process_urls function in a separate thread to avoid blocking the Flask app
    threading.Thread(target=process_urls).start()

    # Start the Flask app
    app.run()
