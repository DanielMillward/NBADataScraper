import math
import time
from nba_api.stats.static import players
from nba_api.stats.endpoints import playergamelog
from nba_api.stats.library.parameters import SeasonAll
import csv
import pandas as pd
from bs4 import BeautifulSoup
import requests
from dateutil.parser import parse
import datetime
from io import StringIO


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
        outtext = (
            "Added data for "
            + row["full_name"]
            + " "
            + str(counter)
            + "/"
            + str(len(players))
        )
        print(outtext)
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
    testing = False
    # get number of pages to iterate through - find start date?
    data = pd.read_csv(data_csv_name)

    data["GAME_DATE"] = data["GAME_DATE"].apply(clean_date)
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
    else:
        print(f"Failed to retrieve content. Status code: {response.status_code}")
        raise ValueError("cant read main page!")

    # for each page
    counter = 0
    all_injuries = pd.DataFrame(columns=["Date", "matching_id", "injury_type"])
    for url in urls:
        out_string = "Adding injury page " + str(counter + 1) + "/" + str(len(urls))
        print(out_string)
        if counter > 3 and testing:
            break
        counter += 1
        # https://www.prosportstransactions.com/basketball/Search/SearchResults.php?Player=&Team=&BeginDate=2022-12-21&EndDate=&InjuriesChkBx=yes&Submit=Search
        # scrape the data and store in dataframe with datetime column
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
        # for each row in injury data, find player and whether it was to injury or not
        # Date, Team, Acquired, Relinquished, Notes
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
        page_df = page_df[page_df["matching_id"].notna()]
        if not all_injuries.empty:
            all_injuries = pd.concat([all_injuries, page_df], ignore_index=True)
        else:
            all_injuries = pd.concat([page_df], ignore_index=True)

        time.sleep(wait_seconds)

    # For row in all injuries:
    all_injuries = all_injuries.sort_values(by="Date")

    for _, injury_row in all_injuries.iterrows():
        # For just the data rows with matching id AND are later:
        ref_date = pd.to_datetime(injury_row["Date"])
        ref_id = int(injury_row["matching_id"])
        ref_injury_type = injury_row["injury_type"]
        filtered_df = data[data["GAME_DATE"] > ref_date]
        filtered_df = data[data["player_id"] == ref_id]
        # Calculate the number of days since the reference date
        for data_idx, data_row in filtered_df.iterrows():
            days_since_injury = (data_row["GAME_DATE"] - ref_date).dt.days
            if days_since_injury < 0:
                data.loc[data_idx, "days_since_last_injury"] = math.inf
            else:
                data.loc[data_idx, "days_since_last_injury"] = days_since_injury
            data.loc[data_idx, "type_of_last_injury"] = ref_injury_type
            print(ref_id, "had an injury")

    data.drop_duplicates(subset=["player_id", "game_id"], inplace=True)
    data.to_csv(data_csv_name, index=False)
    return data_csv_name


def make_time_idx(game_id, min_id):
    return game_id - min_id


def turn_game_id_to_time_idx(data_csv_name):
    data = pd.read_csv(data_csv_name)

    min_game_id = data["game_id"].min()
    data["time_idx"] = data["game_id"].apply(make_time_idx, min_id=min_game_id)

    data.drop_duplicates(subset=["player_id", "game_id"], inplace=True)
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


def clean_up_data(data_csv_name):
    df = df.drop("VIDEO_AVAILABLE", axis=1)


if __name__ == "__main__":
    # only do 3 players for testing
    testing = True

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

    players_csv = get_active_players()
    data_csv_name = instantiate_data_if_needed(data_csv_name, columns)
    data_csv_name = add_nba_api_data(players_csv, data_csv_name, testing)
    data_csv_name = add_injury_data(players_csv, data_csv_name, testing)

    data_csv_name = turn_game_id_to_time_idx(data_csv_name)
    data_csv_name = add_teams_playing_column(data_csv_name)
    data_csv_name = add_which_team_column(data_csv_name)
    data_csv_name = clean_up_data(data_csv_name)
