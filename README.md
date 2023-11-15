# NBADataScraper
Scraping basketball-reference into a local sql database

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
