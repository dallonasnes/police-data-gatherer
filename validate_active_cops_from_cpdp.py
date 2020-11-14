import json
from time import sleep

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

from webdriver_manager.chrome import ChromeDriverManager

"""
Sadly, the API results from cpdp.co don't match the data that is hosted on their website
We consider their website source of truth, not the API results, based on recency of data updates
This program validates API data by comparing it to the data on their website
Particular focus is on if a cop is still active and number of allegations

Input: cops_by_allegation.json from CPDP API
Output: active_cops_by_allegation.json

"""
UNVALIDATED_COPS_ALLEGATION_DATA_LIST = "data/unvalidated_cops_by_allegation.json"
ACTIVE_COPS_ALLEGATION_DATA_LIST = "data/active_cops_by_allegation.json"

def validate_active_cops_from_cpdp():
    scraper = PoliceAllegationDataScraper()
    try:
        scraper.update_allegation_data()
        scraper.write_json()

    except Exception as ex:
        print(ex)

    finally:
        scraper.finish()


class PoliceAllegationDataScraper():
    def __init__(self):
        self.host = "https://cpdp.co"
        with open(UNVALIDATED_COPS_ALLEGATION_DATA_LIST, "r") as handle:
            all_officer_allegation_data_list = json.loads(handle.read())["officers"]
            #filter down to cops still listed as active
            #we trust nonactive to be correct because, if cop wasn't active by the time CPDP API was built, then they stay inactive
            self.active_officer_allegation_data_list = list(filter(
                                                            lambda cop: cop["active"] == "Yes",
                                                            all_officer_allegation_data_list
                                                        ))
        
        options = Options()
        options.add_argument('--headless')
        self.driver = webdriver.Chrome(ChromeDriverManager().install(), chrome_options=options)
        self.wait = WebDriverWait(self.driver, 2)
    
    def update_allegation_data(self):
        for cop in self.active_officer_allegation_data_list:
            self.driver.get(self.host + cop["absolute_url"])
            sleep(2)

            career_span = self.driver.find_elements_by_class_name('summary-field-value')[-1].text
            is_active = 'Present' in career_span

            #if not active, then we don't need to update allegations info
            if not is_active:
                cop["active"] = "No"
                continue

            allegations_count = int(self.driver.find_elements_by_class_name('metrics-pane-value')[0].text)
            cop["allegations_count"] = allegations_count
        

    def write_json(self):
        active_officers_list_to_obj = {"officers": self.active_officer_allegation_data_list}
        active_officer_allegations_as_json = json.dumps(active_officers_list_to_obj)
        with open(ACTIVE_COPS_ALLEGATION_DATA_LIST, "w") as handle:
            handle.write(active_officer_allegations_as_json)


    def finish(self):
        self.driver.quit()


if __name__ == "__main__":
    validate_active_cops_from_cpdp()