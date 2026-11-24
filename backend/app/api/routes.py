from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

from app.services import engine

router = APIRouter()


class CaseUpdate(BaseModel):
    status: str
    analyst_note: str = Field(default="", max_length=4000)


@router.get("/health", tags=["system"])
def health_check():
    engine.init_db()
    return {"status": "ok"}


@router.get("/system/status", tags=["system"])
def system_status():
    engine.init_db()
    return {
        "application": "Banking Fraud & AML Intelligence Platform",
        "stage": "functional_mvp",
        "integrations": {
            "api": "implemented", "database": "sqlite_local",
            "streaming": "simulated_by_seeded_batch",
            "fraud_detection": "explainable_heuristics",
            "aml_detection": "account_funnel_heuristic",
            "xgboost": "not_implemented", "graphsage": "not_implemented"
        }
    }


@router.post("/demo/seed", tags=["demo"])
def seed_demo():
    return engine.seed_demo_data()


@router.post("/analysis/run", tags=["analysis"])
def run_analysis():
    return engine.analyze_all()


@router.get("/dashboard", tags=["dashboard"])
def get_dashboard():
    engine.init_db()
    return engine.dashboard()


@router.get("/transactions", tags=["transactions"])
def get_transactions(
    limit: int = Query(default=200, ge=1, le=500),
    q: str | None = Query(default=None, max_length=100),
    channel: str | None = Query(default=None, pattern="^(UPI|NEFT|IMPS)$"),
    min_amount: float | None = Query(default=None, ge=0),
    max_amount: float | None = Query(default=None, ge=0),
):
    engine.init_db()
    if min_amount is not None and max_amount is not None and min_amount > max_amount:
        raise HTTPException(status_code=422, detail="min_amount cannot exceed max_amount")
    return engine.search_transactions(q, channel, min_amount, max_amount, limit)


@router.get("/transactions/{transaction_id}", tags=["transactions"])
def get_transaction(transaction_id: str):
    engine.init_db()
    transaction = engine.get_transaction(transaction_id)
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return transaction


@router.get("/alerts", tags=["alerts"])
def get_alerts(limit: int = 100):
    engine.init_db()
    return engine.list_rows("alerts", max(1, min(limit, 500)))


@router.post("/alerts/{alert_id}/case", tags=["cases"])
def open_case(alert_id: str):
    case = engine.create_case(alert_id)
    if not case:
        raise HTTPException(status_code=404, detail="Alert not found")
    return case


@router.get("/cases", tags=["cases"])
def get_cases(limit: int = 100):
    engine.init_db()
    return engine.list_rows("cases", max(1, min(limit, 500)))


@router.patch("/cases/{case_id}", tags=["cases"])
def patch_case(case_id: str, update: CaseUpdate):
    try:
        case = engine.update_case(case_id, update.status, update.analyst_note)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc))
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    return case
