from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_predict():
    payload = {"text": "hello"}
    response = client.post("/predict", json=payload)

    assert response.status_code == 200
    assert response.json()["output"] == "olleh"