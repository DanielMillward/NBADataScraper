import pandas as pd
from nba_api.stats.endpoints import playergamelog
from nba_api.stats.library.parameters import SeasonAll
from nba_api.stats.static import teams

# TODO: Add 3 pointers to double double??


def appFunc_double_double(row):
    num_double = 0
    if row["PTS"] >= 10:
        num_double += 1
    if row["REB"] >= 10:
        num_double += 1
    if row["AST"] >= 10:
        num_double += 1
    if row["STL"] >= 10:
        num_double += 1
    if row["BLK"] >= 10:
        num_double += 1

    if num_double >= 2:
        return 1
    return 0


def appFunc_triple_double(row):
    num_double = 0
    if row["PTS"] >= 10:
        num_double += 1
    if row["REB"] >= 10:
        num_double += 1
    if row["AST"] >= 10:
        num_double += 1
    if row["STL"] >= 10:
        num_double += 1
    if row["BLK"] >= 10:
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
    total_score += row["PTS"]
    total_score += row["FG3M"] * 0.5
    total_score += row["REB"] * 1.25
    total_score += row["AST"] * 1.5
    total_score += row["STL"] * 2
    total_score += row["BLK"] * 2
    total_score -= row["TOV"] * 0.5

    total_score += row["double_double"] * 1.5
    total_score += row["triple_double"] * 3

    return total_score


def add_dfs_points(data_csv_name):
    data = pd.read_csv(data_csv_name)
    data["dfs_points"] = data.apply(appFunc_dfs_points, axis=1)
    data.to_csv(data_csv_name, index=False)
    return data_csv_name


def get_team_ids():
    # Retrieve all teams
    nba_teams = teams.get_teams()

    # Extract team IDs
    team_ids = [team["id"] for team in nba_teams]

    return team_ids


player_id = 1629029
gamelogs = pd.concat(
    playergamelog.PlayerGameLog(
        player_id=player_id, season=SeasonAll.all
    ).get_data_frames()
)
# gamelogs = gamelogs.loc[gamelogs["MATCHUP"].str.contains("OKC")]
gamelogs.to_csv("thing.csv", index=False)

data = add_double_triple_double("thing.csv")
data = add_dfs_points(data)

df = pd.read_csv(data)

s2022 = df.loc[df["SEASON_ID"] == 22023]
print(s2022["dfs_points"].mean())
