# Team Charter — Crypto Volatility Detection

## Team Members

| Name | Role | Responsibilities |
|------|------|-----------------|
| Eshita Raj Vegesna | ML Lead | Model training, feature engineering, API design |
| Vaishnavi Athrey Ramesh | Infrastructure Lead | Docker stack, CI/CD, monitoring (Prometheus + Grafana) |
| Litesha Nagendra | Drift & Evaluation | Evidently drift detection, model evaluation, reporting |
| Tejas Goyal | Testing & Docs | Load testing, replay tests, documentation, demo video |

## Project

**Goal:** Build a real-time crypto volatility spike detector using streaming market data, with a production-grade serving stack and monitoring.

## Norms

- All code changes go through pull requests with at least one reviewer.
- `main` branch is always deployable — CI must pass before merge.
- Weekly sync to review progress and blockers.
- All team members contribute to the final demo video.

## Communication

- Primary: Group chat (iMessage / Slack)
- Code: GitHub repository with PR reviews
- Meetings: Weekly 30-min sync

## Decision Log

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-04-20 | Use Eshita's model as base | Best test PR-AUC (0.5598) across all team members |
| 2026-04-20 | XGBoost over neural nets | Faster inference, interpretable, sufficient for tabular features |
| 2026-04-21 | Docker Compose for orchestration | Single-command startup meets rubric requirement |
| 2026-04-22 | prometheus-fastapi-instrumentator | Auto-instruments all endpoints, less boilerplate than manual prometheus_client |
