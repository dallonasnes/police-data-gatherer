import os
import pickle
from datetime import datetime
from time import sleep

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

from webdriver_manager.chrome import ChromeDriverManager

import dateutil

# must add parent dir to python path to make Cop class visible
import sys, inspect

currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0, parentdir)
from cop import Cop

COPS_PICKLE_FILEPATH = "../data/cops.pickle"


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


class PoliceMisconductDataScraper:
    def __init__(self):
        self.output_file = COPS_PICKLE_FILEPATH
        self.url = "https://projects.chicagoreporter.com/settlements/search/officers"
        options = Options()
        # options.add_argument('--headless')
        self.driver = webdriver.Chrome(
            ChromeDriverManager().install(), chrome_options=options
        )
        self.wait = WebDriverWait(self.driver, 2)

    def scrape_cops(self):
        self.driver.get(self.url)
        sleep(1)
        self.driver.find_element_by_xpath("/html/body/div[5]/div/div[2]").click()

        sleep(1)
        self.cops = []
        cops_as_web_elements = self.driver.find_elements_by_class_name("officer")
        for cop in cops_as_web_elements:
            page_url = cop.find_element_by_class_name("officer-link").get_attribute(
                "href"
            )
            details = cop.text.split("\n")
            name = details[0]
            role = details[1]
            total_payments = int(
                details[2].split(" ")[0].split("$")[1].replace(",", "")
            )

            self.cops.append(Cop(name.upper(), role.upper(), total_payments, page_url))

    def scrape_active_status(self):
        for cop in self.cops:
            # have to go to a cop's individual page to see years of active service
            self.driver.get(cop.page_url)
            length_of_service_text = self.driver.find_element_by_class_name(
                "years-of-service"
            ).text
            cop.set_is_active("(active)" in length_of_service_text)
            # TODO: get start date for each cop
            case_list = self.driver.find_element_by_id("officer-case-list")
            cases_descs = case_list.find_elements_by_class_name("case-description")
            case_payments = case_list.find_elements_by_class_name(
                "case-payment-wrapper"
            )
            misconduct_events = {}  # key: date, value: cost
            for idx in range(len(cases_descs)):
                detail_text = (
                    cases_descs[idx].find_element_by_class_name("case-details").text
                )
                date_of_incident = detail_text.split("\n")[3]
                case_payments_detail_string = case_payments[idx].text
                payment_amt = case_payments_detail_string.split("\n")[1]
                misconduct_events[date_of_incident] = payment_amt

    def write_pickle(self):
        with open(self.output_file, "wb") as handle:
            pickle.dump(self.cops, handle)

    def finish(self):
        self.driver.quit()


if __name__ == "__main__":
    scrape_police_misconduct_data()
