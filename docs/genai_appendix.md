# Generative AI Usage Appendix

## Tools Used

- **Claude (Anthropic):** Used for code generation assistance, documentation drafting, Docker configuration, and CI/CD pipeline setup.

## How GenAI Was Used

1. **Docker Compose orchestration:** Claude helped configure the 5-service Docker Compose stack (Kafka, MLflow, API, Prometheus, Grafana) with correct health checks, volume mounts, and service dependencies.

2. **Grafana dashboard JSON:** Claude generated the provisioned Grafana dashboard with panels for request rate, latency percentiles, error rate, and uptime monitoring.

3. **GitHub Actions CI workflow:** Claude created the CI pipeline configuration with lint, test, and Docker build stages.

4. **Documentation:** Claude assisted in drafting the model card, feature spec, runbook, SLO definitions, and this appendix. All content was reviewed and edited by team members.

5. **Test scripts:** Claude helped write the replay test and load test scripts, adapting them to work with Eshita's feature engineering and API format.

## What Was NOT GenAI-Generated

- **Model training code and feature engineering:** Written by Eshita Raj Vegesna based on domain analysis of crypto market microstructure.
- **Data collection pipeline:** Coinbase WebSocket consumer and Kafka producer written by team members.
- **Model selection decision:** Based on empirical metric comparison across all team members' models.
- **Architecture decisions:** Made collaboratively by the team based on course requirements and prior experience.

## Verification

All GenAI-assisted code was reviewed, tested locally, and validated through the CI pipeline before inclusion in the final submission.
