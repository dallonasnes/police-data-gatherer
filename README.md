# Police Data Gatherer

This project has two components - scrapers that run periodically and a restful API that serves the scraped data.

## Local development
Clone this repo. Then create a virtual environment and run `pip install -r requirements.txt`. You're all set. You can run the test suite with `pytest test_client.py` and spin up a local development server with `python api.py`

## Scrapers
In the scrapers directory, `driver.py` orchestrates both scrapers. `misconduct_data_scraper.py` scrapes police misconduct data from ChicagoReporter investigation website. `complaint_data_scraper.py` scrapes complaint data from Cpdp.co. The driver kicks off both of these jobs, then builds a `Cop` object for each officer that stores merged and validated data. Finally, it serializes the collection of objects into a `cops_with_data.pickle` file stored in the `data` directory.

Note that running scrapers requires local chromedriver setup: `https://chromedriver.chromium.org/`

## API Endpoint
`api.py` is an endpoint that serves web and mobile clients. On load, it reads the most recent `cops_with_data.pickle` into memory. It responds to HTTP requests by filtering `cops_with_data` stored in memory.

## Data Sources:
Police complaint data: `https://cpdp.co`

Police misconduct settlement data: `https://projects.chicagoreporter.com/settlements/`

## Deployment
Code formatters run on each commit, to enforce code style and readability. Integration test suite is run on each push.

The `Procfile` instructs Heroku on how to start server. Heroku redeploys on every merge into `main` after integration test suite succeeds. Endpoint host is `police-data-gatherer.herokuapp.com`. Mobile endpoint path is `/cops`.

## Future TODO
1. A cron file to schedule jobs
1. A Dockerfile to support running on different machines
1. Get more CPD data to scrape
1. Add more cities whose data is available
