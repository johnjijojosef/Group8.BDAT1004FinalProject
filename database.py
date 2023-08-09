import requests
from bs4 import BeautifulSoup
import csv
import time
import pymongo 
import urllib.parse

# Set user agent headers to mimic a web browser
headers = {'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/112.0'}

# Function to scrape reviews from a given URL
def get_reviews(url):
    # Extract Yelp Business ID from the given URL
    soup = BeautifulSoup(requests.get(url, headers=headers).content, 'html.parser')
    biz_id_element = soup.find('meta', attrs={"name": "yelp-biz-id"})
    if biz_id_element is None:
        return []

    biz_id = biz_id_element['content']

    # Define the Yelp review feed URL pattern
    review_url = "https://www.yelp.ie/biz/{biz_id}/review_feed?rl=en&q=&sort_by=relevance_desc&start={start}"

    # Initialize an empty list to store the reviews
    reviews = []

    # Loop through multiple pages to retrieve all the reviews (you can increase the range for more reviews)
    for start in range(0, 100, 5):
        r_url = review_url.format(biz_id=biz_id, start=start)
        data = requests.get(r_url, headers=headers).json()
        for r in data['reviews']:
            review_text = BeautifulSoup(r['comment']['text'], 'html.parser').text
            reviews.append(review_text)

    return reviews

def store_reviews_in_database(reviews, db_name):
    username = 'dbuser'
    password = 'Pa$$word@61803'
    escaped_username = urllib.parse.quote_plus(username)
    escaped_password = urllib.parse.quote_plus(password)
    database_url = 'dbcluster1.2v8vfcl.mongodb.net'

    # Create the MongoDB connection URI with the escaped username and password
    uri = f"mongodb+srv://{escaped_username}:{escaped_password}@{database_url}/{db_name}"

    # Connect to your MongoDB using the URI
    client = pymongo.MongoClient(uri)
    db = client[db_name]

    # Collection for the database is added
    collection = db['Collection1']

    # Insert the reviews into the collection
    for review in reviews:
        collection.insert_one(review)

    # Close the database connection
    client.close()


def main():
    with open('url.txt', 'r') as url_file:
        urls = url_file.read().splitlines()

    for url in urls:
        business_name = BeautifulSoup(requests.get(url, headers=headers).content, 'html.parser').find('h1').text.strip()
        reviews = get_reviews(url)

        # Create a list of review dictionaries with business name and review text
        review_list = []
        for review in reviews:
            review_dict = {'Business Name': business_name, 'Review': review}
            review_list.append(review_dict)

        # Store the reviews in the database with the provided database name
        store_reviews_in_database(review_list, 'Database1')


if __name__ == "__main__":
    while True:
        main()
        # Wait for 24 hours before running the script again
        time.sleep(24 * 60 * 60)