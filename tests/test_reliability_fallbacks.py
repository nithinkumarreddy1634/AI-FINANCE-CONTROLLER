"""
Unit tests for API reliability, health checks, and fallback mechanisms.
"""

from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)

def test_component_health_endpoints():
    res = client.get("/health")
    assert res.status_code == 200
    assert res.json()["status"] == "OPERATIONAL"

    res_ai = client.get("/health/ai")
    assert res_ai.status_code == 200

    res_db = client.get("/health/database")
    assert res_db.status_code == 200

    res_rag = client.get("/health/rag")
    assert res_rag.status_code == 200

