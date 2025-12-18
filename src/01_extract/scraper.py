import requests
import json
import time
import random
from bs4 import BeautifulSoup

# Headers to mimic browser
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

def query_forum_json(url):
    """Fetches JSON data from the specified URL."""
    time.sleep(random.uniform(1, 2)) 
    try:
        response = requests.get(url, headers=HEADERS, timeout=30)
        response.raise_for_status() 
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error during request to {url}: {e}")
        return None

def get_post_body(post_id):
    """Fetches the specific body text for a post ID."""
    url = f"https://us.forums.blizzard.com/en/wow/t/{post_id}.json"
    data = query_forum_json(url)
    if data:
        try:
            html_text = data['post_stream']['posts'][0]['cooked']
            soup = BeautifulSoup(html_text, 'html.parser')
            return soup.get_text()
        except (KeyError, IndexError):
            return ""
    return ""

def run_forum_scraper(page_scrape_num):
    """
    Main entry point for the scheduler.
    Scrapes 'n' pages and saves to a JSON file.
    """
    url_format = "https://us.forums.blizzard.com/en/wow/c/community/general-discussion/171/l/latest.json?ascending=false&no_definitions=true&page="
    filtered_data = {}

    for i in range(page_scrape_num):
        print(f"Scraping page {i+1}...")
        forum_data = query_forum_json(url_format + str(i+1))
        
        if not forum_data:
            continue

        topics = forum_data.get('topic_list', {}).get('topics', [])

        for topic in topics:
            post_id = topic['id']
            
            # Skip if already processed or if it's a system message
            if post_id in filtered_data:
                continue
            if topic['posters'][0]['user_id'] == -1:
                continue

            # Store initial metadata
            filtered_data[post_id] = {
                'title': topic['title'],
                'created_at': topic['created_at'],
                'poster_id' : topic['posters'][0]['user_id']
            }

    # Fetch body text for all collected IDs
    for post_id in list(filtered_data.keys()):
        body = get_post_body(post_id)
        filtered_data[post_id]['body_text'] = body

    with open('../../data/raw_data/filtered_data.json', 'w', encoding='utf-8') as json_file:
        json.dump(filtered_data, json_file, indent=4, ensure_ascii=False)
    
    print("Scraping task complete.")
