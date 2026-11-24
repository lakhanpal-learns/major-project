# Banking Fraud & AML Intelligence Platform

An academic decision-support prototype for transaction fraud risk detection and anti-money-laundering (AML) network analysis. The system uses public and/or synthetic data; it is not connected to real banking infrastructure and does not make legal determinations.

## Architecture (target)
- **Web:** Next.js + TypeScript
- **API:** FastAPI + Pydantic
- **Storage:** PostgreSQL
- **Data engineering:** Python / PySpark; Kafka for simulated streaming
- **Fraud model:** XGBoost
- **AML graph:** GraphSAGE experimentation with PyTorch Geometric
- **Analytics:** Power BI (historical reporting)

## Repository status
The first milestone establishes the API and web application skeleton. Advanced integrations (PostgreSQL persistence, Spark, Kafka, XGBoost, GraphSAGE and Power BI) are planned and must not be treated as implemented until their modules and tests are added.

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
```
backend/    FastAPI service
frontend/   Next.js investigator application
docs/       Architecture and implementation notes
```

## Safety and scope
- Use synthetic or appropriately licensed public datasets only.
- Scores are indicators for human review, not proof of fraud or money laundering.
- No real payment authorization, transaction blocking, or confidential customer data.
