# NBADataScraper

## Newest approach

1. Gather data
2. Make a bayesian model for points, assists, rebounds, etc.
3. If not done in step 1, make a single distribution for each player for potential DFS points.
4. Grab DraftKings data - which players are playing, their positions, and their costs.
5. Genetic Algorithm for best lineup, fitness based on 1000 (?) simulations per generation. For each simulation, give each lineup a ranking. At the end, pick the top 50% of lineups. Idk.

Future improvements:
- Make separate models for pts, ast, reb, etc?
- add minutes played as input
- Group by player position
- do stochastic knapsack code for step 5


___

https://www.draftkings.com/help/rules/nba 

Scraping basketball-reference into a local sql database

How to integrate all the data together?
- Data from nba_api
https://github.com/swar/nba_api/tree/master/docs/nba_api/stats/endpoints 
- Data from injury
https://www.prosportstransactions.com/basketball/Search/Search.php

Notes:

- We don't check for games where a player doesn't play since those are marked "out" beforehand. See
https://help.draftkings.com/hc/en-us/articles/4405229777555-What-happens-if-one-of-the-players-in-my-roster-doesn-t-play-or-has-their-game-cancelled-US-


update_db:
- where: local
- takes: past csv file
- output: updated csv file

train_model
- where: Colab
- takes: csv
- output: trained tft model

get_games_data
- where: local
- takes: draftkings competition id?
- output: json of available players + games data

predict_with_model
- where: Colab
- takes: csv, json of available players + games data
- output: json of player scores predictions
- NOTE: Here we do the triple double / double double stuff based on the sampling

- make_lineups
- where: Colab?
- takes: json of player scoures predictions
- output: json of possible lineups

- final_lineup
- where: Colab
- takes: json of possible lineups
- output: json of final lineup
