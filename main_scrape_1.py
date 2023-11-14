import json
from Scrapers.BballReferenceScraper import BballReferenceScraper
import datetime

#json_file_path = "player_list.json"
python_list = None
#with open(json_file_path, 'r') as json_file:
#    data = json.load(json_file)
#    python_list = data

start_date = datetime.date(2022, 12, 25)
# Gets player list if none was given
bball_ref_data = BballReferenceScraper(start_date, player_list=python_list)

# transform to dataframes here...

# Then turn into a json to store for the thingy

#output_json = {}
#output_json['playersDict'] = playersDict.to_json()
# save the output to file