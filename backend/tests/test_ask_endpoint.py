from fastapi.testclient import TestClient
from backend.app.api.main import app


def test_ask_stream_sse():
    client = TestClient(app)
    res = client.post(
        "/ask",
        headers={"Accept": "text/event-stream"},
        json={"question": "Where do the Dursleys live?"},
    )
    assert res.status_code in (200, 503)
    if res.status_code == 200:
        assert res.headers.get("content-type", "").startswith("text/event-stream")
