# Implementation status

## Milestone 1 — foundation
- [x] FastAPI application entry point
- [x] Environment-based configuration
- [x] CORS for local Next.js development
- [x] Health endpoint
- [x] Explicit integration status endpoint
- [x] Next.js investigator workspace shell
- [ ] Automated tests and CI
- [ ] PostgreSQL schema and migrations
- [ ] Transaction simulator and ingestion
- [ ] Fraud feature pipeline and XGBoost training/evaluation
- [ ] AML graph construction and GraphSAGE experiment
- [ ] Risk engine, alerts, and case workflow
- [ ] Simulated streaming and Power BI reporting

## Important boundary
A health response only confirms that the API process responds. It does not prove database, Kafka, Spark, or model readiness. Model outputs will be treated as risk indicators for human investigation, not legal conclusions.
