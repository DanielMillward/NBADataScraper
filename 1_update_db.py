import time
from nba_api.stats.static import players
from nba_api.stats.endpoints import playergamelog
from nba_api.stats.library.parameters import SeasonAll
import csv
import pandas as pd
from bs4 import BeautifulSoup
import requests


def get_active_players():
    filename = "players.csv"
    active_players_array_of_dicts = players.get_active_players()
    field_names = active_players_array_of_dicts[0].keys()
    with open(filename, mode="w", newline="") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=field_names)
        writer.writeheader()
        writer.writerows(active_players_array_of_dicts)

    return filename


def add_nba_api_data(players_csv, data_csv_name, testing, wait_seconds=1):
    data = pd.read_csv(data_csv_name)
    players = pd.read_csv(players_csv)

    counter = 0
    for _, row in players.iterrows():
        # cut short for testing
        if counter > 3:
            break
        counter += 1

        # get the data for the player
        player_id = row["id"]
        gamelogs = pd.concat(
            playergamelog.PlayerGameLog(
                player_id=player_id, season=SeasonAll.all
            ).get_data_frames()
        )
        if len(gamelogs) == 0:
            print("No data for", row["full_name"])

        # have the data, now to add it to the csv.
        for _, gamelog in gamelogs.iterrows():
            already_exists = (gamelog["Player_ID"] == player_id) & (
                data["game_id"] == gamelog["Game_ID"]
            )
            if not any(already_exists):
                to_add = gamelog
                to_add["player_id"] = to_add["Player_ID"]
                to_add["game_id"] = to_add["Game_ID"]
                data = pd.concat([data, pd.DataFrame([to_add])], ignore_index=True)

        # wait before next request to not get rate limited
        data.drop_duplicates(subset=["player_id", "game_id"], inplace=True)
        data.to_csv(data_csv_name, index=False)
        print("Added data for", row["full_name"])
        time.sleep(wait_seconds)

    data = pd.read_csv(data_csv_name)
    data.drop_duplicates(subset=["player_id", "game_id"], inplace=True)
    data.to_csv(data_csv_name, index=False)
    return data_csv_name


def instantiate_data_if_needed(data_csv_name, columns):
    try:
        data = pd.read_csv(data_csv_name)
    except pd.errors.EmptyDataError:
        data = pd.DataFrame()
    for column in columns:
        if column not in data.columns:
            data[column] = 0
    data.to_csv(data_csv_name, index=False)
    return data_csv_name


def add_injury_data(players_csv, data_csv_name, testing, wait_seconds=1):
    # get number of pages to iterate through - find start date?
    data = pd.read_csv(data_csv_name)
    try:
        data["GAME_DATE"] = pd.to_datetime(data["GAME_DATE"], format="%b %d, %Y")
    except:
        data["GAME_DATE"] = pd.to_datetime(data["GAME_DATE"])

    earliest_date = data["GAME_DATE"].min().strftime("%Y-%m-%d")
    players = pd.read_csv(players_csv)

    url = (
        "https://www.prosportstransactions.com/basketball/Search/SearchResults.php?Player=&Team=&BeginDate="
        + earliest_date
        + "&EndDate=&InjuriesChkBx=yes&Submit=Search"
    )
    response = requests.get(url)

    if response.status_code == 200:
        soup = BeautifulSoup(response.content, "html.parser")
        links = soup.find_all(
            "a", href=lambda href: href and "SearchResults.php?Player=&Team=" in href
        )
        urls = [link["href"] for link in links]

        for url in urls:
            print(url)
    else:
        print(f"Failed to retrieve content. Status code: {response.status_code}")
        raise ValueError("cant read main page!")

    # for each page
    counter = 0
    for url in urls:
        if counter > 3:
            break
        counter += 1
        # https://www.prosportstransactions.com/basketball/Search/SearchResults.php?Player=&Team=&BeginDate=2022-12-21&EndDate=&InjuriesChkBx=yes&Submit=Search
        # scrape the data and store in dataframe with datetime column
        url_to_call = "https://www.prosportstransactions.com/basketball/Search/" + url
        if response.status_code == 200:
            response = requests.get(url_to_call)
            soup = BeautifulSoup(response.content, "html.parser")
            table = soup.find("table", class_="datatable center")
            table_dataframes = pd.read_html(str(table), header=0)
            page_df = table_dataframes[0]
        else:
            print("failed to get data for", url)
    # for each row in injury data, find player and whether it was to injury or not
        for _, row in page_df:
            
    # for every row in data with player, if date is later (start from day after!), update days_since_injury
    # AND last_injury_type
    data.to_csv(data_csv_name, index=False)
    return data_csv_name


def turn_game_id_to_time_idx(data_csv_name):
    raise NotImplementedError("do this")


def clean_up_data(data_csv_name):
    raise NotImplementedError("remove columns, etc")


if __name__ == "__main__":
    # only do 3 players for testing
    testing = True

    # get active players, store in a csv
    columns = ["player_id", "game_id", "days_since_injury", "last_injury_type"]
    data_csv_name = "data.csv"

    players_csv = get_active_players()
    data_csv_name = instantiate_data_if_needed(data_csv_name, columns)
    data_csv_name = add_nba_api_data(players_csv, data_csv_name, testing)
    data_csv_name = add_injury_data(players_csv, data_csv_name, testing)

    data_csv_name = turn_game_id_to_time_idx(data_csv_name)
    data_csv_name = clean_up_data(data_csv_name)
