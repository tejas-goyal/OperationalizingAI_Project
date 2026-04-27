# Generative AI Usage Appendix

## Tools Used

- **Claude (Anthropic):** Used for code generation assistance, documentation drafting, Docker configuration, and CI/CD pipeline setup.

## How GenAI Was Used

1. **Docker Compose orchestration:** Claude helped check the 5-service Docker Compose stack (Kafka, MLflow, API, Prometheus, Grafana) with correct health checks, volume mounts, and service dependencies.

2. **Documentation:** Claude assisted in drafting the model card, feature spec, runbook, SLO definitions, and this appendix. All content was reviewed and edited by team members.

3. **Test scripts:** Claude helped write the replay test and load test scripts, adapting them to work with the existing feature engineering and API format.

## Verification

All GenAI-assisted code was reviewed, tested locally, and validated through the CI pipeline before inclusion in the final submission.
