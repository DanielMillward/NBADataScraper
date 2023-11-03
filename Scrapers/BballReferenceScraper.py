import requests
from BaseClasses.BaseScraper import BaseScraper
import string
from bs4 import BeautifulSoup
import time
import random
import json

# https://www.basketball-reference.com/boxscores/202310250LAC.html 
# BETTER: https://www.basketball-reference.com/players/m/maxeyty01/gamelog/2023 
# The '@' means it was not a home game for the player

class BballReferenceScraper(BaseScraper):
    def __init__(self, start_date, player_list=None) -> None:
        super().__init__(start_date, player_list)
        
    def get_pages(self):
        # 1. Iterate through basketball-reference.com/players/a...z, Get all players in bold
        # Get the player URLs\
        data_list = []
        base_url = "https://www.basketball-reference.com/players/"
        for letter in string.ascii_lowercase:
            print(f"{letter}", end="")
            url = f"{base_url}{letter}/"
            response = requests.get(url)

            if response.status_code == 200:
                # You can process the response content here
                print(f"{letter}", end="")
                soup = BeautifulSoup(response.content, "html.parser")
                table = soup.find('table', {'id': 'players'})
                if table:
                    tbody = table.find('tbody')
                    if tbody:
                        rows = tbody.find_all('tr')
                        # Now you can iterate through tr elements and create dictionaries for each row
                        
                        for row in rows:
                            td_elements = row.find(['th'])  # Include both td and th elements
                            tr_elements = row.find_all(['td'])
                            for element in tr_elements:
                                if "2024" in element.get_text():
                                    a_element = td_elements.find('a')
                                    if a_element:
                                        data_list.append("https://www.basketball-reference.com" + a_element['href']) 
                        # data_list now contains dictionaries for each row
                    else:
                        print("No tbody found within the table with id 'players'.")
                else:
                    print("Table with id 'players' not found on the page.")
            else:
                print(f"Failed to retrieve data for letter {letter}")
            sleep_time = random.uniform(0.5, 1.0)
            time.sleep(sleep_time)
        file_path = "player_list.json"
        # Write the list of strings to a JSON file
        with open(file_path, 'w') as json_file:
            json.dump(data_list, json_file)
        self.pages = data_list

