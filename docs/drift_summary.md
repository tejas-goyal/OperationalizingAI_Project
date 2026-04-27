# Drift Detection Summary

## Method

Used Evidently AI's Kolmogorov-Smirnov (KS) test to compare feature distributions between training data and a held-out reference window. All 20 features were evaluated.

## Results

All 20 features showed statistically significant drift (p < 0.05 on KS test). This is expected given:

1. **Short training window:** ~10 minutes of data captures only one market micro-regime.
2. **Cryptocurrency volatility clustering:** BTC/ETH market dynamics shift rapidly; the distribution seen in training data is unlikely to persist.
3. **Time-of-day effects:** Even minutes apart, trading patterns can shift as different market participants enter/exit.

## Top Drifting Features

| Feature | KS Statistic | p-value | Interpretation |
|---------|-------------|---------|---------------|
| `mid_price` | High | < 0.001 | Price level shifted between train/test windows |
| `ret_std_60s` | High | < 0.001 | Volatility regime changed |
| `tick_count_*` | Moderate | < 0.01 | Trading activity level shifted |
| `spread_bps` | Moderate | < 0.01 | Liquidity conditions changed |

## Implications

- **Model retraining** should be triggered when >50% of features show significant drift.
- **Rollback** to the z-score baseline is available as a safety net — the baseline is less sensitive to distribution shift since it only depends on one feature (`ret_std_60s`).
- In production, an Evidently monitoring job should run periodically (e.g., every hour) comparing recent predictions against the training reference.

## Monitoring Setup

Prometheus scrapes the API's `/metrics` endpoint. Grafana dashboards track request latency and throughput, which can serve as indirect drift signals (e.g., if prediction latency spikes or spike_rate deviates significantly from the training spike_rate of 14.8%).
