# Service Level Objectives (SLOs)

## API Availability

- **Target:** 99% uptime during demo window
- **Measurement:** `up{job="crypto-api"}` in Prometheus
- **Alert:** Grafana panel turns red when API is down

## Prediction Latency

- **p50:** < 20ms
- **p95:** < 100ms
- **p99:** < 500ms
- **Measurement:** `http_request_duration_seconds` histogram in Prometheus
- **Verification:** `scripts/load_test.py` with 100 burst requests

## Error Rate

- **Target:** < 1% of /predict requests return 5xx
- **Measurement:** `http_requests_total{status=~"5.."}` / `http_requests_total`
- **Grafana panel:** Error Rate (5xx) time series

## Throughput

- **Target:** > 50 req/s sustained under load test
- **Verification:** Load test output (Req/sec metric)

## Model Quality

- **Test PR-AUC:** > 0.50 (current: 0.5598)
- **Baseline beat:** ML model must exceed z-score baseline on PR-AUC
- **Drift monitoring:** Evidently KS test on all 20 features; alert if > 50% of features show p < 0.05
