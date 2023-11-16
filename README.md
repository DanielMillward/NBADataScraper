# NBADataScraper
Scraping basketball-reference into a local sql database

How to integrate all the data together?
- Data from nba_api
https://github.com/swar/nba_api/tree/master/docs/nba_api/stats/endpoints 
- Data from injury
https://www.prosportstransactions.com/basketball/Search/Search.php

1. Data initialization
- nba_api
2. Additional data
- injury
- years experience at gametime
- nba_api bio stuff

Get_data.py
- filename="data.csv"
- startdate = None
- initial_checkpoint = None
- injury_checkpoint = None
- bio_checkpoint = None
- initial_cols = [blah]
- injury_cols = [days_since_last_dtd_injury,etc.]
- bio_cols = [stuff]
- data = pd.readcsv(filename)
- addcols([initial_cols, injury_cols, bio_cols]) # adds the columns if not exist
- data = add_initial_data(data, filename, startdate, initial_checkpoint) # should read the playerid/gameid combo and update if necessary
- data = add_injury_data(data, filename, startdate, injury_checkpoint)
- data = add_bio_data(data, filename, startdate, bio_checkpoint) # the csv should be autosaved at this point



1. Run get_all_urls, label by year
- Output: all_urls.json
2. Run train_data_scrape, which takes all the years of data and puts in a sql database
- output: sql database
3. Run slap_into_csv which puts sql into a zipped csv. Just a big sql query. Takes date param
- output: zipped csv
4. Run train_model in notebook using zipped csv
- output: trained tft
___
5. Run current_data_scrape, which scrapes only the most recent urls
- output: sql database
6. Run slap_into_csv
- output: csv
7. Run predict_with_model in notebook, download the distributions json, for each individual player category
- output: players_predictions.json
8. Run make_lineups, which makes lineups that maximize probability of being over a set of scores
- output: good_lineups.json
9. Run final_lineup, which does a MCMC kinda thing and see which of the make_lineups lineups has the highest win rate
- output: best_lineup.json
