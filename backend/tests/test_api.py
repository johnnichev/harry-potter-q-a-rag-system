from fastapi.testclient import TestClient
from backend.app.api.main import app


def test_health():
    client = TestClient(app)
    res = client.get("/health")
    assert res.status_code in (200, 503)


def test_ask_bad_request():
    client = TestClient(app)
    res = client.post("/ask", json={"question": ""})
    assert res.status_code in (400, 503)
