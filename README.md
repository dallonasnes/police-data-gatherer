# Police Data Gatherer

This project contains several files.

`Scraper.py` uses selenium to scrape police misconduct settlement data from ChicagoReporter's police misconduct settlement project.
Their data is no longer actively updated so, once run, the pickled output `cops.pickle` is written to disk and from then can be treated as a static file.
Running `scraper.py` requires chromedriver: `https://chromedriver.chromium.org/`

`Data_Aggregator.py` gets police complaint data from `cpdp.co` endpoint. It then reads in `cops.pickle` and takes the intersection to combine police misconduct settlement payout data with filed complaint data for each cop in the list. It writes the output as `cops_with_data.pickle`

`Api.py` is a `FastAPI` endpoint that serves GET requests over HTTP. On load, it reads `cops_with_data.pickle` and stores it as json in memory. It then serves this data for requests at `/cops` endpoint.

Usage is demonstrated in `test_client.py` which you can run with a `pytest` command in the root directory.

## Data Sources:

Police complaint data: (REST API) `https://api.cpdp.co/api/v2/officers/top-by-allegation/`

Police misconduct settlement data: `https://projects.chicagoreporter.com/settlements/search/officers`

## Deploy
The `Procfile` instructs Heroku on how to start server. Heroku redeploys on every merge into `master` branch. Endpoint lives at `police-data-gatherer.heroku.com`