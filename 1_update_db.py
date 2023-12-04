import time
from nba_api.stats.static import players
from nba_api.stats.endpoints import playergamelog
from nba_api.stats.library.parameters import SeasonAll
import csv
import pandas as pd


def get_active_players():
    filename = "players.csv"
    active_players_array_of_dicts = players.get_active_players()
    field_names = active_players_array_of_dicts[0].keys()
    with open(filename, mode="w", newline="") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=field_names)
        writer.writeheader()
        writer.writerows(active_players_array_of_dicts)

    return filename


def add_nba_api_data(players_csv, data_csv_name, wait_seconds=1):
    data = pd.read_csv(data_csv_name)
    players = pd.read_csv(players_csv)

    for _, row in players.iterrows():
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
        data.to_csv(data_csv_name, index=False)
        time.sleep(wait_seconds)


def instantiate_data_if_needed(data_csv_name, columns):
    try:
        data = pd.read_csv(data_csv_name)
    except pd.errors.EmptyDataError:
        data = pd.DataFrame()
    for column in columns:
        if column not in data.columns:
            data[column] = 0
    data.to_csv(data_csv_name, index=False)

def turn_game_id_to_time_idx(data_csv_name):
    raise NotImplementedError("do this")


if __name__ == "__main__":
    # get active players, store in a csv
    columns = ["player_id", "game_id"]
    data_csv_name = "data.csv"

    players_csv = get_active_players()
    instantiate_data_if_needed(data_csv_name, columns)
    data_csv = add_nba_api_data(players_csv, data_csv_name)
    turn_game_id_to_time_idx(data_csv_name)
