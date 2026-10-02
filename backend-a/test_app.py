"""Run with the Backend A virtual environment: python test_app.py."""
from app import app

with app.test_client() as client:
    for path in ("/", "/api/status"):
        response = client.get(path)
        assert response.status_code == 200
        assert response.json["backend"] == "A"
        assert response.headers["X-Backend"] == "A"
    assert client.get("/").json["message"] == "Backend A is running"
    assert client.get("/api/status").json["status"] == "ok"
    for etag, expected in ((None, 200), ('"backend-a-v1"', 304), ('"other"', 200)):
        response = client.get("/api/cache-demo", headers={"If-None-Match": etag} if etag else {})
        assert response.status_code == expected
        assert response.headers["X-Backend"] == "A"
        assert response.headers["Cache-Control"] == "public, max-age=60"
        assert response.headers["ETag"] == '"backend-a-v1"'
        assert response.data == b"" if expected == 304 else response.json["backend"] == "A"
print("PASS: Backend A routes, headers, cache validation, and empty 304 body")
