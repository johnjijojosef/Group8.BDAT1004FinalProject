# Import necessary libraries

import requests

from bs4 import BeautifulSoup

import time

import pymongo

import urllib.parse

 

# Set user agent headers to mimic a web browser

headers = {'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/112.0'}

 

# Function to scrape reviews from a given URL

def get_reviews(url):

    # Extract Yelp Business ID from the given URL

    soup = BeautifulSoup(requests.get(url, headers=headers).content, 'html.parser')  # Fetch the HTML content of the URL and parse it

    biz_id_element = soup.find('meta', attrs={"name": "yelp-biz-id"})  # Find the meta tag with the 'yelp-biz-id' attribute

    if biz_id_element is None:

        return []  # If the Yelp Business ID is not found, return an empty list

 

    biz_id = biz_id_element['content']  # Get the Yelp Business ID from the 'content' attribute of the meta tag


    # Define the Yelp review feed URL pattern

    review_url = "https://www.yelp.ie/biz/{biz_id}/review_feed?rl=en&q=&sort_by=relevance_desc&start={start}"


    # Initialize an empty list to store the reviews

    reviews = []

 

    # Loop through multiple pages to retrieve all the reviews (you can increase the range for more reviews)

    for start in range(0, 100, 5):

        r_url = review_url.format(biz_id=biz_id, start=start)  # Generate the review feed URL with the current start value

        data = requests.get(r_url, headers=headers).json()  # Fetch the JSON data from the Yelp review feed API

        for r in data['reviews']:

            review_text = BeautifulSoup(r['comment']['text'], 'html.parser').text  # Extract the review text from the JSON data

            reviews.append(review_text)  # Append the review text to the list of reviews

 

    return reviews  # Return the list of reviews


def store_reviews_in_database(reviews, db_name):

    # MongoDB database configuration

    username = 'dbuser'  # Replace with your MongoDB username

    password = 'Pa$$word@61803'  # Replace with your MongoDB password

    escaped_username = urllib.parse.quote_plus(username)  # URL encode the username

    escaped_password = urllib.parse.quote_plus(password)  # URL encode the password

    database_url = 'dbcluster1.2v8vfcl.mongodb.net'  # Replace with your MongoDB cluster URL

 

    # Create the MongoDB connection URI with the escaped username and password

    uri = f"mongodb+srv://{escaped_username}:{escaped_password}@{database_url}/{db_name}"

 

    # Connect to your MongoDB using the URI

    client = pymongo.MongoClient(uri)

    db = client[db_name]

 

    # Replace 'Collection1' with the actual name of your collection

    collection = db['Collection1']

 

    # Insert the reviews into the collection

    for review in reviews:

        collection.insert_one(review)

 

    # Close the database connection

    client.close()

 

def main():

    # Read the list of URLs from a file named 'url.txt'

    with open('url.txt', 'r') as url_file:

        urls = url_file.read().splitlines()

 

    # Loop through each URL and process its reviews

    for url in urls:

        # Extract business name from the given URL

        business_name = BeautifulSoup(requests.get(url, headers=headers).content, 'html.parser').find('h1').text.strip()

 

        # Get reviews for the current URL

        reviews = get_reviews(url)

 

        # Create a list of review dictionaries with business name and review text

        review_list = []

        for review in reviews:

            review_dict = {'Business Name': business_name, 'Review': review}

            review_list.append(review_dict)

 

        # Store the reviews in the database with the provided database name

        store_reviews_in_database(review_list, 'Database1')

 

# Execute the main function if this script is run as the main program

if __name__ == "__main__":

    # Run the main function in an infinite loop

    while True:

        try:

            main()

        except Exception as e:

            print("An error occurred:", str(e))


        # Wait for 1 hour before running the script again

        print("Waiting for 1 hour before running the script again...")

        time.sleep(24 * 60 * 60)