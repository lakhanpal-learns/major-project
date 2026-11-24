# Implementation status

## Working MVP
- [x] FastAPI application and health endpoint
- [x] SQLite persistence for customers, accounts, transactions, alerts, and cases
- [x] Deterministic synthetic banking-data generator
- [x] Explainable transaction risk heuristics (amount, UTC hour, flagged device, sender velocity)
- [x] AML funnel-account heuristic (3+ distinct recent senders)
- [x] Dashboard metrics and transaction/alert/case APIs
- [x] Create case from alert; update case status and analyst note
- [x] Next.js investigator dashboard connected to API
- [x] API workflow tests authored

## Not implemented (do not claim otherwise)
- XGBoost model training/inference
- GraphSAGE / graph neural network
- Kafka event streaming
- PySpark distributed processing
- PostgreSQL production persistence
- Power BI report

## Run
Backend: see root README. Frontend: `cd frontend && npm install && npm run dev`.
Set `NEXT_PUBLIC_API_URL` in `frontend/.env.local` if the API is not at the default URL.

## Limitations
Synthetic demo data only. The fraud and AML methods are transparent prototype heuristics, not validated bank-grade detection systems. Scores are investigation leads, not proof of fraud or money laundering.
