"""
Automated unit tests for Phase 4 UI endpoints, CSV/JSON report exports, and Settings.
"""

from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)

def test_summary_reports():
    res_json = client.get("/api/v1/reports/summary/json")
    assert res_json.status_code == 200
    assert "total_records" in res_json.json()

    res_csv = client.get("/api/v1/reports/summary/csv")
    assert res_csv.status_code == 200
    assert "text/csv" in res_csv.headers["content-type"]
    assert "Order ID" in res_csv.text

def test_exceptions_reports():
    res_json = client.get("/api/v1/reports/exceptions/json")
    assert res_json.status_code == 200

    res_csv = client.get("/api/v1/reports/exceptions/csv")
    assert res_csv.status_code == 200
    assert "text/csv" in res_csv.headers["content-type"]

def test_ai_investigations_reports():
    res_json = client.get("/api/v1/reports/ai-investigations/json")
    assert res_json.status_code == 200

    res_csv = client.get("/api/v1/reports/ai-investigations/csv")
    assert res_csv.status_code == 200
    assert "text/csv" in res_csv.headers["content-type"]

def test_audit_reports():
    res_json = client.get("/api/v1/reports/audit/json")
    assert res_json.status_code == 200

    res_csv = client.get("/api/v1/reports/audit/csv")
    assert res_csv.status_code == 200
    assert "text/csv" in res_csv.headers["content-type"]

