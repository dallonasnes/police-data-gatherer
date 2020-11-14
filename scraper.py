import os
import pickle
from time import sleep

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

from webdriver_manager.chrome import ChromeDriverManager

from cop import Cop

COPS_PICKLE_FILEPATH = "data/cops.pickle"

def scrape_police_misconduct_data():
    scraper = PoliceMisconductDataScraper()
    try:
        scraper.scrape_cops()
        scraper.scrape_active_status()
        scraper.write_pickle()
    
    except Exception as ex:
        print(ex)

    finally:
        scraper.finish()

class PoliceMisconductDataScraper():
    def __init__(self):
        self.output_file = COPS_PICKLE_FILEPATH
        self.url = "https://projects.chicagoreporter.com/settlements/search/officers"
        options = Options()
        options.add_argument('--headless')
        self.driver = webdriver.Chrome(ChromeDriverManager().install(), chrome_options=options)
        self.wait = WebDriverWait(self.driver, 2)
    
    def scrape_cops(self):
        self.driver.get(self.url)
        sleep(1)
        self.driver.find_element_by_xpath('/html/body/div[5]/div/div[2]').click()

        sleep(1)
        self.cops = []
        cops_as_web_elements = self.driver.find_elements_by_class_name('officer')
        for cop in cops_as_web_elements:
            page_url = cop.find_element_by_class_name('officer-link').get_attribute('href')
            details = cop.text.split('\n')
            name = details[0]
            role = details[1]
            total_payments = int(details[2].split(' ')[0].split('$')[1].replace(',', ''))

            self.cops.append(Cop(name.upper(), role.upper(), total_payments, page_url))
    
    def scrape_active_status(self):
        for cop in self.cops:
            #have to go to a cop's individual page to see years of active service
            self.driver.get(cop.page_url)
            length_of_service_text = self.driver.find_element_by_class_name('years-of-service').text
            cop.set_is_active('(active)' in length_of_service_text)

    def write_pickle(self):
        with open(self.output_file, "wb") as handle:
            pickle.dump(self.cops, handle)

    def finish(self):
        self.driver.quit()

if __name__ == "__main__":
    scrape_police_misconduct_data()