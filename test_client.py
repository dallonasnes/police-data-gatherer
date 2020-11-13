import json
from typing import List, Dict

from fastapi import FastAPI
from fastapi.testclient import TestClient

from api import app
client = TestClient(app)

def test_read_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"Hello": "World"}

def test_read_all_cops():
    response = client.get("/cops")
    assert response.status_code == 200
    cops: List[Dict] = response.json()["cops"]
    assert len(cops) > 0
    #every cop in this list should have a non-zero complaint count
    for cop in cops:
        assert cop['complaint_count'] > 0

    #assert cops are in descending order by total payments
    for idx in range(len(cops) - 1):
        assert cops[idx]['total_payments'] >= cops[idx]['total_payments']

def test_read_subset_cops():
    count = 10
    response = client.get("/cops/0/" + str(count))
    assert response.status_code == 200
    assert len(response.json()["cops"]) == count

def test_read_subset_cops_validate_math():
    responseA = client.get("/cops/0/10")
    responseB = client.get("/cops/10/10")
    responseC = client.get("/cops/0/20")

    #assert that content of responseA + responseB == responseC
    assert responseA.json()["cops"] + responseB.json()["cops"] == responseC.json()["cops"]

def test_read_subset_cops_no_count_specified_should_fail():
    response = client.get("/cops/5")
    assert response.status_code == 404 #path not found 

def test_read_subset_cops_wrong_type_should_fail():
    response = client.get("/cops/0/d")
    assert response.status_code == 422 #value is not valid integer

def test_read_subset_cops_idx_out_of_range_should_fail():
    response = client.get("/cops/50000000/0")
    assert response.status_code == 404 #start idx out of range

def test_read_subset_cops_nonexistent_path_should_fail():
    response = client.get("/cops/5/2/8")
    assert response.status_code == 404 #path not found