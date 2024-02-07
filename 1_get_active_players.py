from nba_api.stats.static import players
from nba_api.stats.endpoints import commonplayerinfo
import pandas as pd


def get_active_players(player_csv_name, testing):
    """Gets active players with their position and player_id."""

    # store active players in dataframe
    data = pd.DataFrame()
    active_players_array_of_dicts = pd.DataFrame(players.get_active_players())
    data["player_id"] = active_players_array_of_dicts[["id"]]
    data["full_name"] = active_players_array_of_dicts[["full_name"]]

    # get their positions
    data["position"] = " "
    for idx, row in data.iterrows():
        if idx > 3 and testing is True:
            break

        player_info = commonplayerinfo.CommonPlayerInfo(player_id=row["player_id"])
        player_info = player_info.get_normalized_dict()
        position = player_info["CommonPlayerInfo"][0]["POSITION"]
        data.loc[data["player_id"] == row["player_id"], "position"] = position
        outtext = (
            "Added data for "
            + row["full_name"]
            + " "
            + str(idx)
            + "/"
            + str(len(data))
            + " "
        )
        print(" " * 80, end="\r", flush=True)
        print(outtext, end="\r", flush=True)

    data.to_csv(player_csv_name, index=False)

    return player_csv_name


if __name__ == "__main__":
    # only do 3 players for testing
    testing = True
    player_csv_name = "players.csv"

    players_csv = get_active_players(player_csv_name, testing)
