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

def test_read_cops():
    response = client.get("/cops")
    assert response.status_code == 200
    cops: List[Dict] = json.loads(response.json())
    assert len(cops) > 0
    #every cop in this list should have a non-zero complaint count
    for cop in cops:
        assert cop['complaint_count'] > 0