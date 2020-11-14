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
    
    def update_allegation_data(self):
        #using a while loop to retry cops that hit a timeout during the get request
        i = 0
        stuckCounter = 0 #skip one if we're stuck at a single row forever
        while i < len(self.active_officer_allegation_data_list):
            cop = self.active_officer_allegation_data_list[i]
            self.driver.get(self.host + cop["absolute_url"])
            try:
                element = WebDriverWait(self.driver, 5).until(
                    EC.presence_of_element_located((By.XPATH, '//*[@id="root"]/div/div[1]/div/div[2]/div[2]/div[8]/div/span[1]'))
                )
            except:
                #my wifi is bad, so timeouts are inconsistent
                #so to handle the exception, just make the request again and sleep for a bit
                self.driver.get(self.host + cop["absolute_url"])
                sleep(10)
            try:
                career_span = self.driver.find_elements_by_class_name('summary-field-value')[-1].text
                is_active = 'Present' in career_span

                #if not active, then we don't need to update allegations info
                if not is_active:
                    cop["active"] = "No"
                    continue

                allegations_count = int(self.driver.find_elements_by_class_name('metrics-pane-value')[0].text)
                cop["allegations_count"] = allegations_count
                i += 1
                stuckCounter = 0
            except:
                stuckCounter += 1
                if stuckCounter == 10:
                    print("STUCK at url:", self.host + cop["absolute_url"])
                    print("STUCK at cop named:", cop["officer_first"] + " " + cop["officer_last"])
                    i += 1
                    stuckCounter = 0
        

    def write_json(self):
        active_officers_list_to_obj = {"officers": self.active_officer_allegation_data_list}
        active_officer_allegations_as_json = json.dumps(active_officers_list_to_obj)
        with open(ACTIVE_COPS_ALLEGATION_DATA_LIST, "w") as handle:
            handle.write(active_officer_allegations_as_json)


    def finish(self):
        self.driver.quit()


if __name__ == "__main__":
    validate_active_cops_from_cpdp()