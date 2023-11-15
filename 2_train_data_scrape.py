import json
import datetime
from bs4 import BeautifulSoup, Comment

import requests

start_index = 0
json_file_path = "all_urls.json"

array_to_delete = [
    "Rk",
    "G",
    "Date",
    "Age",
    "Tm",
    "",
    "Opp",
    "",
    "GS",
    "MP",
    "FG",
    "FGA",
    "FG%",
    "3P",
    "3PA",
    "3P%",
    "FT",
    "FTA",
    "FT%",
    "ORB",
    "DRB",
    "TRB",
    "AST",
    "STL",
    "BLK",
    "TOV",
    "PF",
    "PTS",
    "GmSc",
    "+/-",
]


def get_raw_data(soup):
    all_data = []

    # find regular season data
    table = soup.find("table", {"id": "pgl_basic"})
    if table:
        rows = []
        for row in table.find_all("tr"):
            # Extract data from each cell in the row
            cells = [cell.text.strip() for cell in row.find_all(["td", "th"])]
            rows.append(cells)
        table_data = {"regular_data": rows}
        all_data.append(table_data)
    else:
        print("No tables with the specified class found.")

    # find playoff data
    comment = soup.find(
        string=lambda text: isinstance(text, Comment) and "pgl_basic_playoffs" in text
    )
    if comment:
        comment_soup = BeautifulSoup(comment, "html.parser")
        playoff_table = comment_soup.find("table", {"id": "pgl_basic_playoffs"})
        rows = []
        for row in playoff_table.find_all("tr"):
            # Extract data from each cell in the row
            cells = [cell.text.strip() for cell in row.find_all(["td", "th"])]
            rows.append(cells)
        table_data = {"playoff_data": rows}
        all_data.append(table_data)

    # find bio data
    outer_div = soup.find("div", {"id": "meta"})
    if outer_div:
        bio_data = outer_div.find("div", {"class": None})
        if bio_data:
            player_data = {"bio_data": str(bio_data)}
            # json_data = json.dump(player_data)
            all_data.append(player_data)
        else:
            print("Inner div without id not found inside the outer div.")
    else:
        print("Outer div with id 'meta' not found.")

    # write it to a file (or just a object later on)
    return all_data


def get_clean_data(raw_data):
    raw_data = remove_headers(raw_data)
    raw_data = blank_to_zeros(raw_data)
    raw_data = incomplete_to_zeros(raw_data)
    # convert 

    with open("temp_data_2.json", "w") as json_file:
        json.dump(raw_data, json_file)


def incomplete_to_zeros(raw_data):
    for group in raw_data:
        if "regular_data" in group:
            for game_index in range(len(group["regular_data"])):
                game = group["regular_data"][game_index]
                if len(game) != 30:
                    game = game[:-1]
                    if len(game) < 30:
                        zeros_needed = 30 - len(game)
                        game += ["0"] * zeros_needed
                    group["regular_data"][game_index] = game

        if "playoff_data" in group:
            for game_index in range(len(group["playoff_data"])):
                game = group["playoff_data"][game_index]
                if len(game) != 30:
                    game = game[:-1]
                    if len(game) < 30:
                        zeros_needed = 30 - len(game)
                        game += ["0"] * zeros_needed
                    group["playoff_data"][game_index] = game
    return raw_data


def blank_to_zeros(raw_data):
    for group in raw_data:
        if "regular_data" in group:
            for i, subarray in enumerate(group["regular_data"]):
                group["regular_data"][i] = [
                    str(element) if element != "" else "0" for element in subarray
                ]
        if "playoff_data" in group:
            for i, subarray in enumerate(group["playoff_data"]):
                group["playoff_data"][i] = [
                    str(element) if element != "" else "0" for element in subarray
                ]
    return raw_data


def remove_headers(raw_data):
    for group in raw_data:
        if "regular_data" in group and isinstance(group["regular_data"], list):
            # Filter out sub-arrays that match the given array
            group["regular_data"] = [
                subarray
                for subarray in group["regular_data"]
                if subarray != array_to_delete
            ]

        if "playoff_data" in group and isinstance(group["playoff_data"], list):
            # Filter out sub-arrays that match the given array
            group["playoff_data"] = [
                subarray
                for subarray in group["playoff_data"]
                if subarray != array_to_delete
            ]
    return raw_data


def add_columns(clean_data):
    raise NotImplementedError()


def add_player_to_db(all_data):
    # all_data only from one url hit
    pass


if __name__ == "__main__":
    # load all urls
    with open(json_file_path, "r") as json_file:
        urls = json.load(json_file)

    # just counting it
    start_index = max(0, min(start_index, len(urls) - 1))
    # go through all the urls
    for i in range(start_index, len(urls)):
        print(str(i) + "...")
        url = urls[i]["url"]
        response = requests.get(url)
        # extract, clean, modify, and add url data to db
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, "html.parser")
            raw_game_data = get_raw_data(soup)
            clean_data = get_clean_data(
                raw_game_data
            )  # put ages correctly, was home team, etc.
            all_data = add_columns(clean_data)
            add_player_to_db(all_data)

        else:
            print(f"Failed to retrieve data for url {url}")
