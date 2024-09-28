import requests
import time
import xml.etree.ElementTree as ET

def get_bgg_data(endpoint, username, params=None):
    base_url = f"https://boardgamegeek.com/xmlapi2/{endpoint}"
    if params is None:
        params = {}
    params['username'] = username
    
    response = requests.get(base_url, params=params)
    
    if response.status_code == 200:
        return response.content
    elif response.status_code == 202:
        print(f"Request for {endpoint} accepted, but still processing. Retrying after a short wait.")
        time.sleep(15)
        return get_bgg_data(endpoint, username, params)
    else:
        print(f"Error: Unable to fetch {endpoint} data. Status code: {response.status_code}")
        return None

def save_to_file(data, filename):
    file_path = "./userdata/" + filename
    with open(file_path, 'wb') as f:
        f.write(data)

def main():
    username = "mark4"
    collection_data = get_bgg_data('collection', username, {'own': 1})
    plays_data = get_bgg_data('plays', username)
    
    # Get collection data
    if collection_data is not None:
        print("Collection data retrieved successfully")
        save_to_file(collection_data, f"collection_{username}.xml")
    else:
        print("Failed to retrieve collection data")
    
    # Get plays data
    if plays_data is not None:
        print("Plays data retrieved successfully")
        save_to_file(plays_data, f"plays_{username}.xml")
    else:
        print("Failed to retrieve plays data")

if __name__ == "__main__":
    main()