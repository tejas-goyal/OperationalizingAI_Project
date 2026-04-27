# Load Test Results

**Date:** April 2026
**Tool:** `scripts/load_test.py` (100 sequential burst requests)
**Target:** `http://localhost:8000/predict`
**Environment:** MacBook Air M2, Docker Desktop, crypto-api container

## Results

```
=== Load Test Results (100 requests) ===
Total time:      1.54s
Successful:      100/100
Errors:          0
Avg latency:     14.2ms
p50 latency:     12.1ms
p95 latency:     44.8ms
p99 latency:     78.3ms
Max latency:     118.5ms
Req/sec:         64.9
```

## SLO Compliance

| SLO | Target | Actual | Status |
|-----|--------|--------|--------|
| p50 latency | < 20 ms | 12.1 ms | PASS |
| p95 latency | < 100 ms | 44.8 ms | PASS |
| Error rate | < 1% | 0% | PASS |
| Throughput | > 50 req/s | 64.9 req/s | PASS |

## Notes

- All requests used the XGBoost ML model variant (not baseline)
- Payload: single-row batch `{"rows": [...]}`  with 20 features
- No warmup period — first request included in measurements
- Docker resource limits: default (no CPU/memory constraints)
