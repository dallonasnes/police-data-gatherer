import os
import pickle
import json

import requests

from cop import Cop
from scraper import scrape_police_misconduct_data, COPS_PICKLE_FILEPATH

COPS_WITH_DATA_PICKLE_FILEPATH = "data/cops_with_data.pickle"
COPS_ALLEGATION_DATA_LIST = "data/cops_by_allegation.json"

class Data():
    def __init__(self):
        self.output_file = COPS_WITH_DATA_PICKLE_FILEPATH
        with open(COPS_PICKLE_FILEPATH, "rb") as handle:
            self.cops = pickle.load(handle)
        
        with open(COPS_ALLEGATION_DATA_LIST, "r") as handle:
            self.officer_allegation_data_list = json.loads(handle.read())["officers"]
        self.officer_allegation_data = {}

    def scrape_police_misconduct_settlement_data(self):
        scrape_police_misconduct_data()

    def get_officer_allegation_data(self):
        for cop in self.officer_allegation_data_list:
            name = (cop['officer_first'] + " " + cop['officer_last']).upper()
            cop_details = {
                "count": int(cop['allegations_count']),
                "active": cop["active"] == "Yes",
                "absolute_url": cop["absolute_url"]
            }
            self.officer_allegation_data[name] = cop_details

    def get_cops_with_payment_and_complaint_data(self):
        cops_with_payment_data = set([cop.name for cop in self.cops])
        cops_names_with_payment_and_complaint_data = cops_with_payment_data.intersection(set(self.officer_allegation_data.keys()))

        self.cops_with_payment_and_complaint_data = []
        for cop in self.cops:
            name = cop.name.upper()
            if name in cops_names_with_payment_and_complaint_data:
                cop_details = self.officer_allegation_data[name]
                cop.set_complaint_count(cop_details["count"])
                cpdp_active_status = cop_details["active"]
                cop.set_is_active(cpdp_active_status if cpdp_active_status == cop.is_active else False)
                cop.set_complaint_page_url("cpdp.co" + cop_details["absolute_url"])
                self.cops_with_payment_and_complaint_data.append(cop)

        #sort from highest to lowest misconduct payouts
        self.cops_with_payment_and_complaint_data = sorted(self.cops_with_payment_and_complaint_data, key= lambda cop: int(cop.total_payments), reverse=True)

    def write_pickle(self):
        with open(self.output_file, "wb") as handle:
            pickle.dump(self.cops_with_payment_and_complaint_data, handle)

if __name__ == "__main__":
    data = Data()
    #don't need to scrape police misconduct settlement data often because host is no longer updated
    if not os.path.isfile(COPS_PICKLE_FILEPATH):
        data.scrape_police_misconduct_settlement_data()
    data.get_officer_allegation_data()
    data.get_cops_with_payment_and_complaint_data()
    data.write_pickle()
