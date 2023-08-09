import requests
from bs4 import BeautifulSoup
import csv
import json

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

# Main function to execute the scraping and save results in a CSV file
def main():
    # Read URLs from the 'url.txt' file and store them in a list
    with open('url.txt', 'r') as url_file:
        urls = url_file.read().splitlines()

    # Open the CSV file to store the extracted reviews
    with open('reviews.csv', 'w', newline='', encoding='utf-8') as csvfile, \
         open('reviews.json', 'w', encoding='utf-8') as jsonfile:

        fieldnames = ['Business Name', 'Review']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        # Write the header row to the CSV file
        writer.writeheader()

        # Initialize an empty list to store reviews for JSON output
        all_reviews = []

        # Loop through each URL to extract reviews and save them in the CSV and JSON files
        for url in urls:
            # Extract the business name from the URL
            business_name = BeautifulSoup(requests.get(url, headers=headers).content, 'html.parser').find('h1').text.strip()

            # Get the reviews for the current URL
            reviews = get_reviews(url)

            # Write each review to the CSV file along with the business name
            for review in reviews:
                writer.writerow({'Business Name': business_name, 'Review': review})

            # Append reviews to the list for JSON output
            all_reviews.extend([{'Business Name': business_name, 'Review': review} for review in reviews])

        # Write all_reviews list to the JSON file
        json.dump(all_reviews, jsonfile, indent=4)


# Execute the main function when running the script                
if __name__ == "__main__":
    main()