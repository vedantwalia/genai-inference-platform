from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_metrics():
    response = client.get("/metrics")
    assert response.status_code == 200
    assert "request_count" in response.text