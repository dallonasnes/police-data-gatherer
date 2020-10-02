import json
import pickle
from typing import List

from fastapi import FastAPI

from cop import Cop
from data_aggregator import COPS_WITH_DATA_PICKLE_FILEPATH

app = FastAPI()

#read pickled data into memory and convert into json
#with open(COPS_WITH_DATA_PICKLE_FILEPATH, "rb") as handle:
#    cops_with_data: List[Cop] = pickle.load(handle)

#singleton since once gathered data is static
#but it may cause performance problems or heroku may not accept it on the free tier
#cops_with_data_as_json = json.dumps([cop.get_dict() for cop in cops_with_data])

@app.get('/')
def read_root():
    return {"Hello": "World"}

@app.get('/cops')
def cops():
    return "can you see this?"
    #return cops_with_data_as_json