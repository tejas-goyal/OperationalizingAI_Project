# Model Card — Crypto Volatility Spike Detector v1.0

## Model Details

- **Model type:** XGBoost binary classifier (`XGBClassifier`)
- **Version:** 1.0.0
- **Trained by:** Eshita Raj Vegesna
- **Date:** April 2026
- **Framework:** XGBoost, scikit-learn
- **Format:** XGBoost JSON (`xgboost_model.json`)

## Intended Use

Detect short-term volatility spikes in cryptocurrency trading pairs (BTC-USD, ETH-USD) using streaming tick data from Coinbase. Designed for educational/research purposes as part of a CMU Heinz College course project.

## Training Data

- **Source:** Coinbase Advanced Trade WebSocket API (public ticker channel)
- **Collection period:** ~10 minutes of live tick data
- **Size:** 21,458 raw ticks → 21,416 feature rows after processing
- **Split:** 60/20/20 time-based (train/val/test)
- **Spike rate:** 14.8% (label = 1 if forward 60s rolling std > 85th percentile threshold τ = 0.000054)

## Features (20)

Computed across 10s, 30s, and 60s time-based sliding windows:
- `ret_mean_{w}s` — mean log return
- `ret_std_{w}s` — std of log returns
- `ret_abs_{w}s` — mean absolute log return
- `tick_count_{w}s` — number of ticks
- `spread_mean_{w}s` — mean bid-ask spread
- `trade_intensity_{w}s` — ticks per second

Plus: `spread_bps` (current spread in basis points), `mid_price` (current mid price)

## Hyperparameters

| Parameter | Value |
|-----------|-------|
| n_estimators | 300 |
| max_depth | 4 |
| learning_rate | 0.05 |
| subsample | 0.8 |
| colsample_bytree | 0.8 |
| scale_pos_weight | ~5.76 (auto from class ratio) |
| eval_metric | aucpr |

## Performance

| Metric | Validation | Test |
|--------|-----------|------|
| PR-AUC | 0.5714 | 0.5598 |
| ROC-AUC | 0.8825 | 0.8746 |
| F1 (0.5 threshold) | 0.0 | 0.0 |
| Best F1 | 0.4516 | 0.4348 |
| Best threshold | 0.00138 | — |

## Baseline Comparison

Z-score rule (ret_std_60s > mean + 1.5*std): Test PR-AUC ~0.35. XGBoost provides ~60% improvement.

## Limitations

- Trained on a short data window (~10 minutes); may not generalize to different market regimes.
- Spike threshold (85th percentile) is data-dependent; needs recalibration on new data.
- No cross-pair features; treats each pair independently.
- Latency-sensitive: features must be computed within the sliding window to remain valid.

## Ethical Considerations

- Not intended for live trading decisions without human oversight.
- Model predictions should be treated as signals, not trading recommendations.
- See AI Use Case & Ethics Canvases in `docs/` for detailed ethical analysis.
