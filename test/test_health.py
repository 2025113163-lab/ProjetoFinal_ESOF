from fastapi.testclient import TestClient

from src.main import app

client = TestClient(app)


def test_health_devuelve_ok():
    response = client.get("/health", headers={"X-Request-ID": "req-test-123"})
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
    assert response.headers.get("X-Request-ID") == "req-test-123"