from nba_api.stats.static import teams
from nba_api.stats.endpoints import leaguegamefinder


# Function to get team ID
def get_team_id(team_name):
    nba_teams = teams.get_teams()
    team = next((team for team in nba_teams if team["full_name"] == team_name), None)
    if team:
        return team["id"]
    else:
        return None


# Function to get NBA Finals games for a specific season
def get_nba_finals_games(season):
    # Get all NBA teams
    nba_teams = teams.get_teams()

    # Create an empty list to store NBA Finals games
    nba_finals_games = []

    for team in nba_teams:
        team_id = team["id"]

        # Use the leaguegamefinder endpoint to get games for a specific team and season
        game_finder = leaguegamefinder.LeagueGameFinder(
            team_id_nullable=team_id,
            season_nullable=season,
            season_type_nullable="Playoffs",
        )
        games = game_finder.get_data_frames()[0]

        # Filter games for the NBA Finals
        finals_games = games[games["MATCHUP"].str.contains("NBA Finals")]

        # Add NBA Finals games to the list
        nba_finals_games.extend(finals_games.to_dict("records"))

    return nba_finals_games


if __name__ == "__main__":
    # Specify the season you're interested in (e.g., '2022-23')
    target_season = "2022-23"

    # Get NBA Finals games for the specified season
    nba_finals_games = get_nba_finals_games(target_season)

    # Display the NBA Finals games
    for game in nba_finals_games:
        print(game)
