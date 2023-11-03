import json
from Scrapers.BballReferenceScraper import BballReferenceScraper
import datetime

json_file_path = "player_list.json"
python_list = None
with open(json_file_path, 'r') as json_file:
    # Load the JSON data from the file
    data = json.load(json_file)
    python_list = data

start_date = datetime.date(2022, 12, 25)
bball_ref_data = BballReferenceScraper(start_date, player_list=python_list)

