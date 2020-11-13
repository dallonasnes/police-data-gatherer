import json
import pickle
from typing import List

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.encoders import jsonable_encoder
from fastapi.templating import Jinja2Templates

from cop import Cop
from data_aggregator import COPS_WITH_DATA_PICKLE_FILEPATH

app = FastAPI()

templates = Jinja2Templates(directory="templates")

#read pickled data into memory as a singleton
with open(COPS_WITH_DATA_PICKLE_FILEPATH, "rb") as handle:
    cops_with_data: List[Cop] = [cop.get_dict() for cop in pickle.load(handle) if cop.is_active]

@app.get('/', response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("frontend.html", {"request": request, "cops_with_data": cops_with_data})

@app.get('/cops')
def cops():
    cops_with_data_as_json = jsonable_encoder(cops_with_data)
    return {"cops": cops_with_data_as_json}

@app.get('/cops/{start_idx}/{count}')
def cops_subset(start_idx: int, count: int):
    response = {"cops": []}
    end_idx = start_idx + count
    if end_idx < len(cops_with_data):
        response["cops"] = jsonable_encoder(cops_with_data[start_idx:end_idx])
        return response
    elif start_idx < len(cops_with_data):
        response["cops"] = jsonable_encoder(cops_with_data[start_idx:])
        return response
    else:
        raise HTTPException(status_code=404, detail="start_idx out of range")