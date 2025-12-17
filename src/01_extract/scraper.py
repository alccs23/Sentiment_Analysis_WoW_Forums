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
    """Fetches JSON data from the specified URL and returns the content."""
    
    time.sleep(random.uniform(1,3)) 

    try:
        response = requests.get(url, headers=HEADERS, timeout=30)
        
        response.raise_for_status() 
        
        data = response.json()
        
        return data
    
    except requests.exceptions.RequestException as e:
        print(f"Error during request: {e}")
        return None
    
def add_posts(json_data, cur_dict):
    """
    Adds a post's title, creation date, and original poster's user ID 
    to a dictionary using the post's ID as the key.

    If the post ID already exists in the dictionary, no action is taken.

    Args:
        json_data (dict): A dictionary containing post data, 
                          including 'id', 'title', 'created_at', and 'posters'.
        cur_dict (dict): The dictionary to which the post information 
                         will be added or checked against.
    """
    post_id = json_data['id']

    # Check if the post_id is already a key in cur_dict
    if post_id in cur_dict:
        pass
    # if poster_id == -1 it was a system message that should not be included in dataset
    elif json_data['posters'][0]['user_id'] == -1:
        pass
    else:
        cur_dict[post_id] = {
            'title': json_data['title'],
            'created_at': json_data['created_at'],
            # OP is always at position 0 in posters category
            'poster_id' : json_data['posters'][0]['user_id']
        }

def add_post_information(post_id, cur_dict):
    """
    Fetches a forum post's JSON data, extracts the clean body text,
    and updates the provided dictionary with the text.
    """
    url = f"https://us.forums.blizzard.com/en/wow/t/{post_id}.json"
    data = query_forum_json(url)

    html_text = data['post_stream']['posts'][0]['cooked']

    soup = BeautifulSoup(html_text, 'html.parser')

    plain_text = soup.get_text()

    cur_dict[post_id]['body_text'] = plain_text


if __name__ == "__main__":

    url_format = "https://us.forums.blizzard.com/en/wow/c/community/general-discussion/171/l/latest.json?ascending=false&no_definitions=true&page="

    page_scrape_num = 1

    for i in range(page_scrape_num):

        forum_data = query_forum_json(url_format + str(i+1))

            
        #Dict that will contain post_id keys and as values important information I want to keep
        filtered_data = {}

        for n in range(30):
            add_posts(forum_data['topic_list']['topics'][n], filtered_data)
        
        for post_id in filtered_data:
            add_post_information(post_id, filtered_data)

        with open('filtered_data.json', 'w', encoding='utf-8') as json_file:
            json.dump(filtered_data, json_file, indent=4, ensure_ascii=False)

        
        