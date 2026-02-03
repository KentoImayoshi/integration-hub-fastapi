from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_health_ok():
    r = client.get("/health")
    assert r.status_code == 200
    data = r.json()
    assert data["status"] == "ok"


def test_create_job_rejects_unknown_connector():
    r = client.post("/jobs", json={"connector_name": "nope", "payload": {"msg": "x"}})
    assert r.status_code == 400
    assert "Unknown connector" in r.json()["detail"]


def test_create_job_accepts_echo_connector():
    r = client.post("/jobs", json={"connector_name": "echo", "payload": {"msg": "ok"}})
    assert r.status_code == 200
    data = r.json()
    assert "job_id" in data
    assert data["status"] == "PENDING"
    assert data["attempt"] == 1
