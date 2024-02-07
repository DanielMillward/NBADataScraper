import datetime
from nba_api.stats.endpoints import leaguegamefinder
import pandas as pd
from nba_api.stats.static import teams


def get_game_ids(season):
    # Initialize the game finder object
    game_finder = leaguegamefinder.LeagueGameFinder(season_nullable=season)

    # Perform the search
    games = game_finder.get_data_frames()[0]
    team_ids = get_team_ids()
    games = games.loc[games["TEAM_ID"].isin(team_ids)]
    return games


def get_team_ids():
    # Retrieve all teams
    nba_teams = teams.get_teams()

    # Extract team IDs
    team_ids = [team["id"] for team in nba_teams]

    return team_ids


# Example usage:
if __name__ == "__main__":
    season = "2022-23"  # Change this to your desired season

    games = get_game_ids(season)
    result = games.drop_duplicates(subset=["GAME_ID"])
    print("Total Game IDs found for season {}: {}".format(season, len(result)))
    result.to_csv("test.csv", index=False)
