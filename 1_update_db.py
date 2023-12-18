import math
import sys
import time
from nba_api.stats.static import players
from nba_api.stats.endpoints import playergamelog
from nba_api.stats.library.parameters import SeasonAll
from nba_api.stats.endpoints import leaguegamefinder
import csv
import pandas as pd
from bs4 import BeautifulSoup
import requests
from dateutil.parser import parse
import datetime
from io import StringIO
import tqdm


def get_active_players(player_csv_name):
    active_players_array_of_dicts = players.get_active_players()
    field_names = active_players_array_of_dicts[0].keys()
    with open(player_csv_name, mode="w", newline="") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=field_names)
        writer.writeheader()
        writer.writerows(active_players_array_of_dicts)

    return player_csv_name


def add_nba_api_data(players_csv, data_csv_name, testing, wait_seconds=1):
    data = pd.read_csv(data_csv_name)
    players = pd.read_csv(players_csv)

    counter = 0
    for _, row in players.iterrows():
        # cut short for testing
        if counter > 3 and testing:
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
        outtext = (
            "Added data for "
            + row["full_name"]
            + " "
            + str(counter)
            + "/"
            + str(len(players))
            + " "
        )
        print(" " * 80, end="\r", flush=True)
        print(outtext, end="\r", flush=True)
        time.sleep(wait_seconds)
    print()
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


def clean_date(text):
    return parse(text)


def find_matching_id(injury_row, keyword_df):
    for _, row in keyword_df.iterrows():
        if row["full_name"] in injury_row["Relinquished"]:
            if "DTD" in injury_row["Notes"]:
                return (row["id"], "DTD")
            else:
                return (row["id"], "Not DTD")
    return None, None


def add_injury_data(players_csv, data_csv_name, testing, wait_seconds=1):
    # get correct date data
    data = pd.read_csv(data_csv_name)
    data["GAME_DATE"] = data["GAME_DATE"].apply(clean_date)
    data["GAME_DATE"] = pd.to_datetime(data["GAME_DATE"])

    # make initial url request
    earliest_date = data["GAME_DATE"].min().strftime("%Y-%m-%d")
    players = pd.read_csv(players_csv)
    url = (
        "https://www.prosportstransactions.com/basketball/Search/SearchResults.php?Player=&Team=&BeginDate="
        + earliest_date
        + "&EndDate=&InjuriesChkBx=yes&Submit=Search"
    )
    response = requests.get(url)

    # get all page links
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, "html.parser")
        links = soup.find_all(
            "a", href=lambda href: href and "SearchResults.php?Player=&Team=" in href
        )
        urls = [link["href"] for link in links]
    else:
        print(f"Failed to retrieve content. Status code: {response.status_code}")
        raise ValueError("cant read main page!")

    # for each page, scrape relevant data
    counter = 0
    all_injuries = pd.DataFrame(columns=["Date", "matching_id", "injury_type"])
    for url in urls:
        out_string = ("Adding injury page " + str(counter + 1) + "/" + str(len(urls)) + " ")
        print(out_string, end="\r")
        if counter > 3 and testing:
            break
        counter += 1
        # https://www.prosportstransactions.com/basketball/Search/SearchResults.php?Player=&Team=&BeginDate=2022-12-21&EndDate=&InjuriesChkBx=yes&Submit=Search
        # call page, read table & add clean date
        url_to_call = "https://www.prosportstransactions.com/basketball/Search/" + url
        if response.status_code == 200:
            response = requests.get(url_to_call)
            soup = BeautifulSoup(response.content, "html.parser")
            table = soup.find("table", class_="datatable center")
            table_dataframes = pd.read_html(StringIO(str(table)), header=0)
            page_df = table_dataframes[0]
            page_df["Date"] = pd.to_datetime(page_df["Date"].apply(clean_date))
        else:
            print("failed to get data for", url)
        # If find player match in a row, add matching id and injury type in page_df
        page_df["matching_id"] = None
        page_df["injury_type"] = None
        for injury_index, injury_row in page_df.iterrows():
            for _, row in players.iterrows():
                if isinstance(injury_row["Relinquished"], str) and isinstance(
                    injury_row["Notes"], str
                ):
                    if row["full_name"] in injury_row["Relinquished"]:
                        if "DTD" in injury_row["Notes"]:
                            page_df.at[injury_index, "matching_id"] = row["id"]
                            page_df.at[injury_index, "injury_type"] = "DTD"
                        else:
                            page_df.at[injury_index, "matching_id"] = row["id"]
                            page_df.at[injury_index, "injury_type"] = "Not DTD"

        # add injuries to all_injuries
        page_df = page_df[page_df["matching_id"].notna()]
        if not all_injuries.empty:
            all_injuries = pd.concat([all_injuries, page_df], ignore_index=True)
        else:
            all_injuries = pd.concat([page_df], ignore_index=True)

        time.sleep(wait_seconds)

    # For row in all injuries, update relevant rows in data
    all_injuries = all_injuries.sort_values(by="Date")
    for _, injury_row in all_injuries.iterrows():
        # Find just the data rows matching the injury player_id AND are later:
        ref_date = pd.to_datetime(injury_row["Date"])
        ref_id = int(injury_row["matching_id"])
        ref_injury_type = injury_row["injury_type"]
        filtered_df = data[data["GAME_DATE"] > ref_date]
        filtered_df = data[data["player_id"] == ref_id]
        # Calculate the number of days since the reference date & update data
        print("Adding injuries to data...")
        for data_idx, data_row in filtered_df.iterrows():
            days_since_injury = (data_row["GAME_DATE"] - ref_date).days
            if days_since_injury < 0:
                data.loc[data_idx, "days_since_last_injury"] = math.inf
            else:
                data.loc[data_idx, "days_since_last_injury"] = days_since_injury
            data.loc[data_idx, "type_of_last_injury"] = ref_injury_type

    # fillna
    data["days_since_last_injury"] = data["days_since_last_injury"].fillna(math.inf)
    data["type_of_last_injury"] = data["type_of_last_injury"].fillna(math.inf)

    print()
    data.drop_duplicates(subset=["player_id", "game_id"], inplace=True)
    data.to_csv(data_csv_name, index=False)
    return data_csv_name


def make_time_idx(game_id, min_id):
    return game_id - min_id


def turn_game_id_to_time_idx(data_csv_name):
    data = pd.read_csv(data_csv_name)

    data["game_id_str"] = data["game_id"].astype(str).str[1:]

    data = data.sort_values(by="game_id_str")

    data["time_idx"] = range(len(data))

    del data["game_id_str"]
    data.to_csv(data_csv_name, index=False)

    return data_csv_name


def apply_home(matchup):
    if "vs." in matchup:
        return matchup.split(" vs. ")[0]
    elif "@" in matchup:
        return matchup.split(" @ ")[1]


def apply_away(matchup):
    if "vs." in matchup:
        return matchup.split(" vs. ")[1]
    elif "@" in matchup:
        return matchup.split(" @ ")[0]


def add_teams_playing_column(data_csv_name):
    """Add home and away team columns"""
    data = pd.read_csv(data_csv_name)
    data["home_team"] = data["MATCHUP"].apply(apply_home)
    data["away_team"] = data["MATCHUP"].apply(apply_away)

    data.drop_duplicates(subset=["player_id", "game_id"], inplace=True)
    data.to_csv(data_csv_name, index=False)
    return data_csv_name


def apply_which_team(matchup):
    if "vs." in matchup:
        return matchup.split(" vs. ")[0]
    elif "@" in matchup:
        return matchup.split(" @ ")[0]


def add_which_team_column(data_csv_name):
    data = pd.read_csv(data_csv_name)
    data["team"] = data["MATCHUP"].apply(apply_which_team)
    data["was_home"] = False
    data.loc[data["team"] == data["home_team"], "was_home"] = True

    data.drop_duplicates(subset=["player_id", "game_id"], inplace=True)
    data.to_csv(data_csv_name, index=False)
    return data_csv_name


def apply_game_type(season_id):
    first_digit = str(season_id)[0]
    switch_dict = {
        "1": "preseason",
        "2": "regular",
        "3": "allstar",
        "4": "postseason",
        "5": "playin",
    }

    return switch_dict.get(first_digit, "Unknown")


def add_game_type(data_csv_name):
    # https://github.com/swar/nba_api/issues/220
    # 1 = pre season
    # 2 = regular
    # 3 = all star
    # 4 = finals/playoffs, post-season
    # 5 = play-in

    data = pd.read_csv(data_csv_name)
    data["game_type"] = data["SEASON_ID"].apply(apply_game_type)

    data.to_csv(data_csv_name, index=False)
    return data_csv_name


def clean_up_data(data_csv_name):
    data = pd.read_csv(data_csv_name)
    data = data.drop("VIDEO_AVAILABLE", axis=1)

    data.to_csv(data_csv_name, index=False)
    return data_csv_name


if __name__ == "__main__":
    # only do 3 players for testing
    testing = False

    # get active players, store in a csv
    columns = [
        "player_id",
        "game_id",
        "days_since_last_injury",
        "type_of_last_injury",
        "home_team",
        "away_team",
        "team",
        "was_home",
    ]
    data_csv_name = "data.csv"
    player_csv_name = "players.csv"

    players_csv = get_active_players(player_csv_name)
    #data_csv_name = instantiate_data_if_needed(data_csv_name, columns)
    #data_csv_name = add_nba_api_data(players_csv, data_csv_name, testing)
    data_csv_name = add_injury_data(players_csv, data_csv_name, testing)

    data_csv_name = turn_game_id_to_time_idx(data_csv_name)
    data_csv_name = add_teams_playing_column(data_csv_name)
    data_csv_name = add_which_team_column(data_csv_name)
    data_csv_name = add_game_type(data_csv_name)
    # add was finals??
    data_csv_name = clean_up_data(data_csv_name)
