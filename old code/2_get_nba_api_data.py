import time
from nba_api.stats.endpoints import playergamelog
from nba_api.stats.library.parameters import SeasonAll
import pandas as pd
from dateutil.parser import parse


def add_nba_api_data(players_csv, data_csv_name, columns, testing, wait_seconds=1):
    """Does a fresh check of all nba players' stats"""
    data = pd.DataFrame(columns=columns)
    players = pd.read_csv(players_csv)

    counter = 0
    for _, row in players.iterrows():
        # cut short for testing
        if counter > 3 and testing:
            break
        counter += 1

        # get the data for the player
        player_id = row["player_id"]
        gamelogs = pd.concat(
            playergamelog.PlayerGameLog(
                player_id=player_id, season=SeasonAll.all
            ).get_data_frames()
        )
        if len(gamelogs) == 0:
            print("No data for", row["full_name"])

        # have the data, now to add it to the csv.
        temp_new_rows = []
        for _, gamelog in gamelogs.iterrows():
            new_row_data = [
                gamelog["Player_ID"],
                gamelog["Game_ID"],
                gamelog["GAME_DATE"],
                gamelog["PTS"],
                gamelog["FG3M"],
                gamelog["REB"],
                gamelog["AST"],
                gamelog["STL"],
                gamelog["BLK"],
                gamelog["TOV"],
            ]
            new_row = pd.DataFrame([new_row_data], columns=columns)
            data = pd.concat([data, new_row], ignore_index=True)

        # wait before next request to not get rate limited
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


def appFunc_double_double(row):
    num_double = 0
    if row["points"] >= 10:
        num_double += 1
    if row["rebounds"] >= 10:
        num_double += 1
    if row["assists"] >= 10:
        num_double += 1
    if row["steals"] >= 10:
        num_double += 1
    if row["blocks"] >= 10:
        num_double += 1

    if num_double >= 2:
        return 1
    return 0


def appFunc_triple_double(row):
    num_double = 0
    if row["points"] >= 10:
        num_double += 1
    if row["rebounds"] >= 10:
        num_double += 1
    if row["assists"] >= 10:
        num_double += 1
    if row["steals"] >= 10:
        num_double += 1
    if row["blocks"] >= 10:
        num_double += 1

    if num_double >= 3:
        return 1
    return 0


def add_double_triple_double(data_csv_name):
    data = pd.read_csv(data_csv_name)
    data["double_double"] = data.apply(appFunc_double_double, axis=1)
    data["triple_double"] = data.apply(appFunc_triple_double, axis=1)
    data.to_csv(data_csv_name, index=False)
    return data_csv_name


def appFunc_dfs_points(row):
    total_score = 0
    total_score += row["points"]
    total_score += row["3_pointers"] * 0.5
    total_score += row["rebounds"] * 1.25
    total_score += row["assists"] * 1.5
    total_score += row["steals"] * 2
    total_score += row["blocks"] * 2
    total_score -= row["turnovers"] * 0.5

    total_score += row["double_double"] * 1.5
    total_score += row["triple_double"] * 3

    return total_score


def add_dfs_points(data_csv_name):
    data = pd.read_csv(data_csv_name)
    data["dfs_points"] = data.apply(appFunc_dfs_points, axis=1)
    data.to_csv(data_csv_name, index=False)
    return data_csv_name


if __name__ == "__main__":
    testing = True
    columns = [
        "player_id",
        "game_id",
        "date",
        "points",
        "3_pointers",
        "rebounds",
        "assists",
        "steals",
        "blocks",
        "turnovers",
    ]
    data_csv_name = "bayesdata.csv"
    players_csv = "data/players.csv"

    add_nba_api_data(players_csv, data_csv_name, columns, testing, wait_seconds=1)
