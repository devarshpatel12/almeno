from fastapi.testclient import TestClient
from ..main import app
import io

client = TestClient(app)


def test_health():
    r = client.get("/health/")
    assert r.status_code == 200


def test_upload_invalid_type():
    files = {"file": ("test.txt", io.BytesIO(b"notcsv"), "text/plain")}
    r = client.post("/jobs/upload", files=files)
    assert r.status_code == 400
