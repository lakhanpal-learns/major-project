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
