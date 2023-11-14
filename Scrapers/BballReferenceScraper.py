import requests
from BaseClasses.BaseScraper import BaseScraper
import string
from bs4 import BeautifulSoup
import time
import random
import json
import re

# https://www.basketball-reference.com/boxscores/202310250LAC.html
# BETTER: https://www.basketball-reference.com/players/m/maxeyty01/gamelog/2023
# The '@' means it was not a home game for the player


class BballReferenceScraper(BaseScraper):
    def __init__(self, start_date, player_list=None) -> None:
        super().__init__(start_date, player_list)

    def get_pages(self):
        # 1. Iterate through basketball-reference.com/players/a...z, Get all players in bold
        # Get the player URLs\
        base_url = "https://www.basketball-reference.com/players/"
        player_urls = self.get_player_urls(base_url, sleep_lower=0.5, sleep_higher=1, start="s")
        game_log_urls_list = []
        raw_urls = []

        for url in player_urls:
            response = requests.get(url)
            output = {}
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, "html.parser")
                game_logs = self.get_game_log(soup, url)
                output = {"id": self.get_player_id(url), "game_logs": game_logs}
                game_log_urls_list.append(output)
                raw_urls.extend(game_logs)
            time.sleep(1)
            print(self.get_player_id(url))
            file_path = "player_list2.json"
            try:
                with open(file_path, 'r') as file:
                    existing_data = json.load(file)
            except FileNotFoundError:
                pass  # File doesn't exist yet
            existing_data.append(output)
            with open(file_path, 'w') as file:
                json.dump(existing_data, file, indent=4)

            print("Data saved to", file_path)
        self.pages = raw_urls

    def page_scrape(self, url):
        pass
        # get page id
        pattern = r"/players/([a-z]+)/([a-z0-9]+)\.html"
        player_id = re.search(pattern, url).group(2)
        if not player_id:
            print("Could not get id for", url)

        # get the gamelog urls

        time.sleep(0.5)
        # for each url, grab the data

        # return data, page_id
        return None, player_id

    def get_game_log(self, soup, url):
        player_id = self.get_player_id(url)
        unordered_lists = soup.find_all("ul", {"class": ""})
        found_urls = False
        log_urls = []
        for list in unordered_lists:
            urls = [
                item.a["href"]
                for item in list.find_all("li")
                if item.a and "/gamelog/" in item.a.get("href", "")
            ]
            for url in urls:
                # print(url)
                log_urls.append(url)
            if urls:
                found_urls = True
                break
        if not found_urls:
            print("Could not find game URLs for:", player_id)
        return log_urls

    def get_player_id(self, url):
        pattern = r"/players/([a-z]+)/([a-z0-9]+)\.html"
        player_id = re.search(pattern, url).group(2)
        if not player_id:
            print("Could not get id for", url)
        return player_id

    def get_player_urls(
        self,
        base_url,
        sleep_lower=1,
        sleep_higher=2,
        start="a",
    ):
        data_list = []
        for letter_code in range(ord(start), ord("z") + 1):
            letter = chr(letter_code)
            url = f"{base_url}{letter}/"
            response = requests.get(url)

            if response.status_code == 200:
                # You can process the response content here
                print(f"{letter}", end="")
                soup = BeautifulSoup(response.content, "html.parser")
                table = soup.find("table", {"id": "players"})
                if table:
                    tbody = table.find("tbody")
                    if tbody:
                        rows = tbody.find_all("tr")
                        # Now you can iterate through tr elements and create dictionaries for each row

                        for row in rows:
                            td_elements = row.find(
                                ["th"]
                            )  # Include both td and th elements
                            tr_elements = row.find_all(["td"])
                            for element in tr_elements:
                                if "2024" in element.get_text():
                                    a_element = td_elements.find("a")
                                    if a_element:
                                        data_list.append(
                                            "https://www.basketball-reference.com"
                                            + a_element["href"]
                                        )
                        # data_list now contains dictionaries for each row
                    else:
                        print("No tbody found within the table with id 'players'.")
                else:
                    print("Table with id 'players' not found on the page.")
            else:
                print(f"Failed to retrieve data for letter {letter}")

            sleep_time = random.uniform(sleep_lower, sleep_higher)
            time.sleep(sleep_time)
        return data_list
