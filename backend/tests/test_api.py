from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_root_returns_application_name():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["message"] == "Banking Fraud & AML Intelligence Platform"


def test_health_endpoint():
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_system_status_is_explicit_about_models():
    response = client.get("/api/v1/system/status")
    assert response.status_code == 200
    integrations = response.json()["integrations"]
    assert integrations["database"] == "sqlite_local"
    assert integrations["xgboost"] == "not_implemented"
    assert integrations["graphsage"] == "not_implemented"


def test_transaction_search_filters_and_detail():
    client.post("/api/v1/demo/seed")
    filtered = client.get("/api/v1/transactions", params={
        "q": "TAML001", "channel": "IMPS", "min_amount": 40000, "max_amount": 50000
    })
    assert filtered.status_code == 200
    rows = filtered.json()
    assert len(rows) == 1
    assert rows[0]["id"] == "TAML001"
    assert rows[0]["from_customer_name"] == "Kabir Singh"

    detail = client.get("/api/v1/transactions/TAML001")
    assert detail.status_code == 200
    assert detail.json()["to_account"] == "A004"

    invalid_range = client.get("/api/v1/transactions", params={
        "min_amount": 50000, "max_amount": 10000
    })
    assert invalid_range.status_code == 422


def test_demo_seed_and_investigation_workflow():
    seeded = client.post("/api/v1/demo/seed")
    assert seeded.status_code == 200
    dashboard = client.get("/api/v1/dashboard").json()
    assert dashboard["transactions"] >= 180
    assert dashboard["alerts"] > 0

    alerts = client.get("/api/v1/alerts").json()
    alert_id = alerts[0]["id"]
    case = client.post(f"/api/v1/alerts/{alert_id}/case")
    assert case.status_code == 200
    case_id = case.json()["id"]

    updated = client.patch(f"/api/v1/cases/{case_id}", json={
        "status": "investigating", "analyst_note": "Reviewing transaction context"
    })
    assert updated.status_code == 200
    assert updated.json()["status"] == "investigating"
