from fastapi import APIRouter

router = APIRouter()


@router.get("/health", tags=["system"])
def health_check() -> dict[str, str]:
    """Liveness check; does not claim database or model readiness."""
    return {"status": "ok"}


@router.get("/system/status", tags=["system"])
def system_status() -> dict:
    """Explicitly report which integrations are not wired yet."""
    return {
        "application": "Banking Fraud & AML Intelligence Platform",
        "stage": "foundation",
        "integrations": {
            "api": "implemented",
            "database": "not_connected",
            "streaming": "not_connected",
            "fraud_model": "not_implemented",
            "aml_graph_model": "not_implemented",
        },
    }
