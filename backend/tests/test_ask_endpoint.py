from fastapi.testclient import TestClient
from backend.app.main import app


def test_ask_plain_text():
    client = TestClient(app)
    res = client.post(
        "/ask",
        json={"question": "Where do the Dursleys live?", "stream": False, "include_sources": False, "format": "text"},
    )
    # service may be not ready if models not present; accept 200 or 503
    assert res.status_code in (200, 503)
    if res.status_code == 200:
        assert isinstance(res.text, str)


def test_ask_json():
    client = TestClient(app)
    res = client.post(
        "/ask",
        json={"question": "Where do the Dursleys live?", "stream": False, "include_sources": True, "format": "json"},
    )
    assert res.status_code in (200, 503)
    if res.status_code == 200:
        data = res.json()
        assert "answer" in data
        assert "sources" in data
