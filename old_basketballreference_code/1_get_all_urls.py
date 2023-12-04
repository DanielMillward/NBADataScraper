import json
from Scrapers.BballReferenceScraper import BballReferenceScraper
import datetime

json_file_path = "player_list.json"
python_list = None
with open(json_file_path, "r") as json_file:
    data = json.load(json_file)
    python_list = data

# Gets initial url list if none was given
bball_ref_data = BballReferenceScraper(None, player_list=python_list)

import json

# Read the input JSON file
with open(json_file_path, "r") as file:
    data = json.load(file)

# Process the data and create a new list of dictionaries
result = []
for entry in data:
    id = entry["id"]
    game_logs = entry["game_logs"]

    for game_log in game_logs:
        year = game_log.split("/")[-1]
        result.append({"year": year, "url": "https://www.basketball-reference.com"+game_log})

# Write the result to a new JSON file
with open("all_urls.json", "w") as file:
    json.dump(result, file, indent=2)

print("Conversion completed. Result saved in 'all_urls.json'.")
