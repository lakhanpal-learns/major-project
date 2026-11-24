# Banking Fraud & AML Intelligence Platform

Decision-support software for transaction monitoring, fraud-risk triage, AML pattern detection and investigation case management.

## Current implementation

- FastAPI backend and Next.js investigator interface.
- SQLite persistence for local development.
- Automatic local dataset initialization when the API starts; the interface does not require a manual seed action.
- Transaction search and detail inspection.
- Explainable rule-based transaction risk checks and account-funnel pattern checks.
- Alert review and case lifecycle management.

## Data-source boundary

The local environment currently initializes generated transaction records so the complete workflow can be exercised without bank credentials. These records are not live banking data. No bank, payment network, or external transaction provider is connected. To process real activity, configure an authorized provider or licensed dataset and implement its adapter; never submit confidential banking data without authorization.

Risk scores are indicators for human review, not proof of fraud or money laundering.

## Planned integrations (not yet implemented)

PostgreSQL production persistence, Kafka event streaming, PySpark processing, XGBoost model inference/training, GraphSAGE graph learning, and Power BI reporting. These must not be represented as active integrations until implemented and tested.

## Run locally

### API
```bash
cd backend
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```
API docs: http://127.0.0.1:8000/docs

### Web
```bash
cd frontend
npm install
npm run dev
```
Web app: http://localhost:3000

## Project structure

- `backend/`: FastAPI service, SQLite persistence and risk engine
- `frontend/`: Next.js investigator application
- `docs/`: architecture and implementation notes
