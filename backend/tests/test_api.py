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


def test_system_status_does_not_claim_unbuilt_integrations():
    response = client.get("/api/v1/system/status")
    assert response.status_code == 200
    integrations = response.json()["integrations"]
    assert integrations["api"] == "implemented"
    assert integrations["database"] == "not_connected"
    assert integrations["fraud_model"] == "not_implemented"
    assert integrations["aml_graph_model"] == "not_implemented"
