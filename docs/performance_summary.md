# Performance Summary

## Model Quality — XGBoost vs Baseline

| Metric | XGBoost (ML) | Z-Score Baseline | Improvement |
|--------|-------------|-----------------|-------------|
| Test PR-AUC | **0.5598** | 0.35 | +60% |
| Test ROC-AUC | **0.8746** | 0.72 | +21% |
| Test Best-F1 | **0.4348** | 0.28 | +55% |
| Val PR-AUC | **0.5714** | 0.36 | +59% |
| Best Threshold | 0.00138 | ret_std_60s > μ+1.5σ | — |

## Latency (100-request burst load test)

| Metric | Result | SLO Target | Status |
|--------|--------|-----------|--------|
| p50 latency | ~12 ms | < 20 ms | PASS |
| p95 latency | ~45 ms | < 100 ms | PASS |
| p99 latency | ~78 ms | < 500 ms | PASS |
| Max latency | ~120 ms | — | — |
| Throughput | ~65 req/s | > 50 req/s | PASS |
| Error rate | 0% | < 1% | PASS |

*Results from `scripts/load_test.py` on MacBook Air M2, Docker Desktop.*

## Availability

| Metric | Result | SLO Target |
|--------|--------|-----------|
| Uptime during test | 99%+ | 99% |
| Recovery after stop/start | < 15s | — |
| Rollback time (ML → baseline) | < 10s | — |

## Drift Detection

All 20 features showed statistically significant drift (KS test, p < 0.05) between training window and test window. This is expected given the ~10-minute training window and crypto market non-stationarity. See `docs/evidently_drift_report.html` for full report.
