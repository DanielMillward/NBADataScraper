# NBADataScraper
Scraping basketball-reference into a local sql database

How to integrate all the data together?
- Data from nba_api
https://github.com/swar/nba_api/tree/master/docs/nba_api/stats/endpoints 
- Data from injury
https://www.prosportstransactions.com/basketball/Search/Search.php

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

- make_lineups
- where: Colab?
- takes: json of player scoures predictions
- output: json of possible lineups

- final_lineup
- where: Colab
- takes: json of possible lineups
- output: json of final lineup
